from typing import List

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.ideation import Ideation


async def increment_view_count(db: AsyncSession, id: int, user_id: int):
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
        .where(Ideation.id == id, Ideation.user_id != user_id)
        .values(view_count=Ideation.view_count + 1)
    )
    await db.commit()


async def fetch_themes(db: AsyncSession, items: List[str] = None):
    if items:
        clauses = [Ideation.theme == item for item in items]
    else:
        clauses = [True]
    themes_query = select(Ideation.theme).where(clauses).distinct()
    themes_result = await db.execute(themes_query)
    return themes_result.scalars().all()
