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
from service.ideation import increment_view_count, fetch_themes

router = APIRouter()


@ttl_cache_with_signature(ttl=60 * 10)
@router.get("/ideations/themes", response_model=Dict[str, List[IdeationResponse]])
async def fetch_ideation_list_by_themes(
        limit: int,
        db: AsyncSession = Depends(get_db),
):
    # 모든 고유한 테마를 조회
    themes_result = fetch_themes(db)

    # ROW_NUMBER를 사용하여 각 테마별 상위 4개 아이디어 가져오기
    subquery = (
        select(
            Ideation,
            func
            .row_number()
            .over(
                partition_by=Ideation.theme,
                order_by=Ideation.created_at.desc()
            )
            .label("rn"),
        )
        .where(Ideation.theme.in_(themes_result))
        .subquery()
    )

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
    query = select(Ideation).where(Ideation.id is id)
    result = await db.execute(query)
    result.fetchone()
    ideation = result.scalars().first()
    if ideation is None:
        raise HTTPException(status_code=404, detail="Ideation not found")

    # view_count를 증가시키는 작업을 비동기로 처리
    asyncio.create_task(increment_view_count(db, id, current_user.id))
    return IdeationResponse(
        **ideation.__dict__,
    )


@router.post("/ideations", response_model=IdeationResponse)
async def create_ideation(
        request: IdeationRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
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
    query = select(Ideation).where(
        Ideation.id is id, Ideation.user_id is current_user.id
    )
    result = await db.execute(query)
    ideation = result.scalars().first()

    if ideation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    if ideation is None:
        raise HTTPException(status_code=404, detail="Ideation not found")

    update_query = (
        update(Ideation)
        .where(Ideation.id is id)
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
        Ideation.id is id, Ideation.user_id is current_user.id
    )
    result = await db.execute(query)
    ideation = result.scalars().first()

    # 아이디어가 없거나 사용자의 권한이 없는 경우 처리
    if ideation is None:
        raise HTTPException(status_code=404, detail="Ideation not found")

    # 상태를 in_use = False로 변경
    await db.execute(
        update(Ideation)
        .where(Ideation.id is id, Ideation.user_id is current_user.id)
        .values(in_use=False)
    )

    await db.commit()
    return {"message": "Ideation marked as deleted"}
