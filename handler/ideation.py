import asyncio
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from common.cache import ttl_cache_with_signature
from database import get_db
from model.ideation import Ideation
from model.user import User
from schema.ideation import IdeationRequest, IdeationResponse

router = APIRouter()


@ttl_cache_with_signature(ttl=60 * 10)
@router.get(
    "/ideations/themes", response_model=Dict[str, List[IdeationResponse]]
)
async def fetch_ideation_list_by_themes(
    limit: int,
    db: AsyncSession = Depends(get_db),
):
    """
    주어진 테마 수와 각 테마당 아이디어 수를 기준으로 아이디어를 가져옵니다.

    Args:
        limit (int): 테마당 가져올 최대 아이디어 수

    Returns:
        dict: 각 테마별 아이디어 목록 딕셔너리
              { 'theme_name': [ideation_object_1, ideation_object_2, ...] }
    """
    # 모든 고유한 테마를 조회
    themes_query = select(Ideation.theme).distinct()
    themes_result = await db.execute(themes_query)
    themes_result.scalars().all()

    # ROW_NUMBER를 사용하여 각 테마별 상위 4개 아이디어 가져오기
    subquery = select(
        Ideation,
        func.row_number()
        .over(partition_by=Ideation.theme, order_by=Ideation.created_at.desc())
        .label("rn"),
    ).subquery()

    # 상위 4개의 아이디어를 선택
    query = select(subquery).where(subquery.c.rn <= limit)

    result = await db.execute(query)
    ideations = result.scalars().all()

    # 결과를 각 테마별로 그룹화
    theme_ideations = {}
    for ideation in ideations:
        if ideation.theme not in theme_ideations:
            theme_ideations[ideation.theme] = []
        theme_ideations[ideation.theme].append(ideation)

    return theme_ideations


@router.get("/ideations/{id}", response_model=IdeationResponse)
async def get_ideation(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    주어진 아이디어 ID를 기준으로 아이디어를 가져옵니다.

    Args:
        id (int): 아이디어 ID

    Returns:
        IdeationResponse: 아이디어 객체
    """
    result = await db.execute(select(Ideation).where(Ideation.id == id))
    ideation = result.scalars().first()
    if ideation is None:
        raise HTTPException(status_code=404, detail="Ideation not found")

    # view_count를 증가시키는 작업을 비동기로 처리
    asyncio.create_task(_increment_view_count(db, id, current_user.id))
    return IdeationResponse(
        **ideation.__dict__,
    )


@router.post("/ideations", response_model=IdeationResponse)
async def create_ideation(
    request: IdeationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    아이디어를 생성합니다.

    Args:
        request (IdeationResponse): 생성할 아이디어 정보

    Returns:
        IdeationResponse: 생성된 아이디어 객체
    """
    ideation = Ideation(
        **request.dict(),
        user=current_user,
    )
    db.add(ideation)
    await db.commit()
    await db.refresh(ideation)
    return IdeationResponse(
        **ideation.__dict__,
    )


@router.put("/ideations/{id}", response_model=IdeationResponse)
async def update_ideation(
    id: str,
    request: IdeationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    주어진 아이디어 ID에 대해 아이디어를 업데이트합니다.

    Args:
        request (IdeationResponse): 업데이트할 아이디어 정보

    Returns:
        IdeationResponse: 업데이트된 아이디어 객체
    """

    query = select(Ideation).where(
        Ideation.id == id, Ideation.user_id == current_user.id
    )
    result = await db.execute(query)
    ideation = result.scalars().first()

    if ideation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    if ideation is None:
        raise HTTPException(status_code=404, detail="Ideation not found")

    update_query = (
        update(Ideation)
        .where(Ideation.id == id)
        .values(**request.dict(exclude_unset=True))
    )
    await db.execute(update_query)
    await db.commit()
    await db.refresh(ideation)
    return IdeationResponse(
        **ideation.__dict__,
    )


@router.delete("/ideations/{id}", status_code=204)
async def delete_ideation(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    주어진 아이디어 ID에 대해 아이디어를 삭제합니다.

    Args:
        id (int): 아이디어 ID
    """
    # 아이디어 조회
    query = select(Ideation).where(
        Ideation.id == id, Ideation.user_id == current_user.id
    )
    result = await db.execute(query)
    ideation = result.scalars().first()

    # 아이디어가 없거나 사용자의 권한이 없는 경우 처리
    if ideation is None:
        raise HTTPException(status_code=404, detail="Ideation not found")

    # 상태를 in_use = False로 변경
    await db.execute(
        update(Ideation)
        .where(Ideation.id == id, Ideation.user_id == current_user.id)
        .values(in_use=False)
    )

    await db.commit()
    return {"message": "Ideation marked as deleted"}


async def _increment_view_count(db: AsyncSession, id: int, user_id: int):
    """
    주어진 아이디어 ID에 대해 view_count를 증가시킵니다.
    본인의 아이디어를 조회하는 경우 view_count를 증가시키지 않습니다.

    Args:
        db (AsyncSession): 데이터베이스 세션.
        id (str): 아이디어 ID.
        user_id (str): 현재 사용자 ID.
    """
    await db.execute(
        update(Ideation)
        .where(Ideation.id == id and Ideation.user_id != user_id)
        .values(view_count=Ideation.view_count + 1)
    )
    await db.commit()
