from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from auth import get_current_user
from database import enforcer, get_db
from model.ideation import Ideation, Theme, Status
from model.user import User
from schema.attachment import AttachmentResponse
from schema.ideation import IdeationRequest, IdeationResponse, ThemeResponse
from schema.invest import InvestmentResponse
from service.ideation import find_theme_by_id, find_ideation_by_id
from service.repository import CrudRepository, get_repository
from utils.path_util import save_image, save_file

router = APIRouter(tags=["아이디어"])


@router.get("/themes", response_model=List[ThemeResponse])
async def get_themes(
        theme_id: Optional[str] = None,
        repo: CrudRepository = Depends(get_repository),
):
    clauses = None
    if theme_id:
        clauses = and_(Theme.id == theme_id)
    themes = await repo.fetch_all(Theme, limit=100, clauses=clauses)
    return [ThemeResponse.model_validate(theme) for theme in themes]


# TODO order 적용, 전체 ideation 조회
@router.get(
    "/ideation/themes", response_model=Dict[str, List[IdeationResponse]]
)
# @cache(expire=60 * 10)
async def fetch_ideation_list_by_themes(
        theme_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db),
        repo: CrudRepository = Depends(get_repository),
):
    # 모든 고유한 테마를 조회
    themes_result = await get_themes(theme_id, repo)

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
            selectinload(Ideation.user),
            selectinload(Ideation.investments),
        )
    )

    result = await db.execute(query)
    ideations = result.unique().scalars().all()

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
        current_user: User = Depends(get_current_user),
        ideation: Ideation = Depends(find_ideation_by_id),
):
    if current_user.id != ideation.user_id:
        ideation.view_count += 1
    return IdeationResponse.model_validate(ideation)


@router.post("/ideation", response_model=IdeationResponse)
async def create_ideation(
        request: Request,
        title: str = Form(...),
        content: str = Form(...),
        theme_id: str = Form(...),
        presentation_date: Optional[datetime] = Form(None),
        close_date: Optional[datetime] = Form(None),
        status: Optional[Status] = Form(Status.BEFORE_START),
        images: List[UploadFile] = File(None),
        files: Optional[List[UploadFile]] = File(None),

        repo: CrudRepository = Depends(get_repository),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    ideation = Ideation(
        title=title,
        content=content,
        presentation_date=presentation_date,
        close_date=close_date,
        status=status,
        user_id=current_user.id,
    )
    ideation.theme = await find_theme_by_id(theme_id, db)
    ideation.images = [] if not images else [await save_image(image, ideation.id, request) for image in images]
    ideation.attachments = [] if not files else [await save_file(f, ideation.id) for f in files]
    ideation = await repo.create(ideation)
    await enforcer.add_policies([(current_user.id, ideation.id, "write")])

    response = IdeationResponse.model_validate(ideation)
    response.images = [AttachmentResponse.model_validate(i) for i in ideation.images]
    response.attachments = [AttachmentResponse.model_validate(a) for a in ideation.attachments]
    return response


@router.put("/ideation/{ideation_id}", response_model=IdeationResponse)
async def update_ideation(
        ideation_id: str,
        request: IdeationRequest = Depends(),
        ideation: Ideation = Depends(find_ideation_by_id),
        theme: Theme = Depends(find_theme_by_id),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation_id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")

    ideation.theme = theme
    for key, value in request.dict(exclude_unset=True).items():
        if value and hasattr(ideation, key):
            setattr(ideation, key, value)
    return IdeationResponse.model_validate(ideation)


@router.delete(
    "/ideations/{ideation_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_ideation(
        ideation: Ideation = Depends(find_ideation_by_id),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not enforcer.enforce(current_user.id, ideation.id, "write"):
        raise HTTPException(status_code=403, detail="Permission denied")
    await db.delete(ideation)

