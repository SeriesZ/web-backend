from collections import defaultdict
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from auth import get_current_user
from database import enforcer, get_db
from handler.attachment import get_attachments, get_comments
from model.ideation import Ideation, Theme
from model.user import User
from schema.ideation import IdeationRequest, IdeationResponse, ThemeResponse
from schema.invest import InvestmentResponse
from service.repository import CrudRepository, get_repository

router = APIRouter(tags=["아이디어"])


@router.get("/themes", response_model=List[ThemeResponse])
async def get_themes(
    theme_name: Optional[str] = None,
    repo: CrudRepository = Depends(get_repository),
):
    clauses = None
    if theme_name:
        clauses = and_(Theme.name == theme_name)
    themes = await repo.fetch_all(Theme, limit=100, clauses=clauses)
    return [ThemeResponse.model_validate(theme) for theme in themes]


# TODO order 적용, 전체 ideation 조회
@router.get(
    "/ideation/themes", response_model=Dict[str, List[IdeationResponse]]
)
@cache(expire=60 * 10)
async def fetch_ideation_list_by_themes(
    theme_name: Optional[str] = None,
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    repo: CrudRepository = Depends(get_repository),
):
    # 모든 고유한 테마를 조회
    themes_result = await get_themes(theme_name, repo)

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
        .where(Ideation.theme_id.in_([theme.id for theme in themes_result]))
        .subquery()
    )

    # 2. 메인 쿼리: 상위 N개의 id를 가진 Ideation 엔티티 및 조인된 데이터 가져오기
    query = (
        select(Ideation)
        .where(
            Ideation.id.in_(
                select(subquery.c.id).where(
                    subquery.c.rn <= offset + limit, subquery.c.rn > offset
                )
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
        theme = ThemeResponse.model_validate(ideation.theme)
        investments = [
            InvestmentResponse.model_validate(i) for i in ideation.investments
        ]

        ideation_props = ideation.__dict__
        ideation_props["theme"] = theme
        ideation_props["investments"] = investments
        res = IdeationResponse.model_validate(ideation_props)
        theme_ideations[ideation.theme.name].append(res)

    return theme_ideations


@router.get("/ideation/{ideation_id}", response_model=IdeationResponse)
async def get_ideation(
    ideation_id: str,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    ideation = await repo.find_by_id(Ideation, ideation_id)

    if current_user.id != ideation.user_id:
        ideation.view_count += 1

    result = dict(
        **ideation.__dict__,
        attachments=await get_attachments(ideation_id, repo),
        comments=await get_comments(ideation_id, repo),
    )
    return IdeationResponse.model_validate(result)


# TODO form에서 file upload 따로
@router.post("/ideation", response_model=IdeationResponse)
async def create_ideation(
    request: IdeationRequest,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    ideation = Ideation(**request.dict())
    ideation.user_id = current_user.id
    ideation = await repo.create(ideation)
    await enforcer.add_policies([(current_user.id, ideation.id, "write")])
    return IdeationResponse.model_validate(ideation)


@router.put("/ideation/{ideation_id}", response_model=IdeationResponse)
async def update_ideation(
    ideation_id: str,
    request: IdeationRequest,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation_id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    ideation = Ideation(**request.dict(), id=ideation_id)
    ideation = await repo.update(ideation)
    return IdeationResponse.model_validate(ideation)


@router.delete(
    "/ideations/{ideation_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_ideation(
    ideation_id: str,
    repo: CrudRepository = Depends(get_repository),
    current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation_id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    await repo.delete(Ideation(id=ideation_id))
