from fastapi import Depends
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status
from starlette.exceptions import HTTPException

from database import AsyncSessionLocal, get_db
from model.ideation import Ideation, Theme


async def increment_view_count(ideation_id: str, user_id: str):
    """
    FIXME session, user 별로 중복을 제외해야 하므로 디자인 다시;;
    주어진 아이디어 ID에 대해 view_count를 증가시킵니다.
    본인의 아이디어를 조회하는 경우 view_count를 증가시키지 않습니다.

    Args:
        db (AsyncSession): 데이터베이스 세션.
        ideation_id (str): 아이디어 ID.
        user_id (str): 현재 사용자 ID.
    """
    async with AsyncSessionLocal() as db:
        async with db.begin():  # 트랜잭션 시작
            result = await db.execute(
                update(Ideation)
                .where(Ideation.id == ideation_id, Ideation.user_id != user_id)
                .values(view_count=Ideation.view_count + 1)
            )


async def find_ideation_by_id(
        ideation_id: str,
        db: AsyncSession = Depends(get_db),
) -> Ideation:
    query = (
        select(Ideation)
        .options(
            joinedload(Ideation.theme),  # Theme 테이블 조인
            joinedload(Ideation.user),  # User 테이블 조인
            joinedload(Ideation.investments),  # Investment 테이블 조인
            joinedload(Ideation.attachments),  # Attachment 테이블 조인
            joinedload(Ideation.comments),  # Comment 테이블 조인
        )
        .where(Ideation.id == ideation_id)
    )
    result = await db.execute(query)
    ideation = result.unique().scalar_one_or_none()
    if not ideation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ideation({ideation_id}) not found",
        )
    return ideation


async def find_theme_by_id(
        theme_id: str,
        db: AsyncSession = Depends(get_db),
):
    # theme_id = request.theme_id
    query = select(Theme).where(Theme.id == theme_id)
    result = await db.execute(query)
    theme = result.unique().scalar_one_or_none()
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme({theme_id}) not found",
        )
    return theme
