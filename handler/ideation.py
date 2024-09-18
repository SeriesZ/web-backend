from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from auth import get_current_user
from common.cache import ttl_cache_with_signature
from database import get_db
from model.ideation import Ideation
from model.user import User
from schema.ideation import IdeationRequest, IdeationResponse
from service.ideation import fetch_themes

router = APIRouter()


@ttl_cache_with_signature(ttl=60 * 10)
@router.get(
    "/ideations/themes", response_model=Dict[str, List[IdeationResponse]]
)
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
            func.row_number()
            .over(
                partition_by=Ideation.theme,
                order_by=Ideation.created_at.desc(),
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


@router.get("/ideations/{ideation_id}", response_model=IdeationResponse)
async def get_ideation(
    ideation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ideation = await db.execute(
        select(Ideation).where(
            Ideation.id == ideation_id, Ideation.in_use.is_(True)
        )
    )
    ideation = ideation.scalars().first()
    if not ideation:
        raise HTTPException(status_code=404, detail="Ideation not found")

    if current_user.id != ideation.user_id:
        ideation.view_count += 1
    return IdeationResponse.model_validate(ideation)


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
    return IdeationResponse.model_validate(ideation)


@router.put("/ideations/{ideation_id}", response_model=IdeationResponse)
async def update_ideation(
    ideation_id: str,
    request: IdeationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Ideation).where(
            Ideation.id == ideation_id,
            Ideation.user_id == current_user.id,
        )
    )
    ideation = result.scalars().first()

    if ideation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    if not ideation:
        raise HTTPException(status_code=404, detail="Ideation not found")

    for key, value in request.dict(exclude_unset=True).items():
        setattr(ideation, key, value)
    await db.commit()
    await db.refresh(ideation)
    return IdeationResponse.model_validate(ideation)


@router.delete(
    "/ideations/{ideation_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_ideation(
    ideation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Ideation).where(
            Ideation.id == ideation_id,
            Ideation.user_id == current_user.id,
        )
    )
    ideation = result.scalars().first()

    if not ideation:
        raise HTTPException(status_code=404, detail="Ideation not found")

    ideation.in_use = False
    return Response(status_code=status.HTTP_204_NO_CONTENT)
