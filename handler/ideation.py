from collections import defaultdict
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
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
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    # 모든 고유한 테마를 조회
    themes_result = await fetch_themes(db)

    # 1. 서브쿼리: 각 테마별 상위 N개의 id 가져오기
    subquery = (
        select(
            Ideation.id,
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

    # 2. 메인 쿼리: 상위 N개의 id를 가진 Ideation 엔티티 및 조인된 데이터 가져오기
    query = (
        select(Ideation)
        .where(
            Ideation.id.in_(
                select(subquery.c.id).where(subquery.c.rn <= limit)
            )
        )
        .options(
            selectinload(Ideation.user), selectinload(Ideation.investments)
        )
    )

    result = await db.execute(query)
    ideations = result.scalars().all()
    # 결과를 각 테마별로 그룹화
    theme_ideations = defaultdict(list)
    for ideation in ideations:
        res = IdeationResponse.model_validate(ideation)
        theme_ideations[ideation.theme].append(res)

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
