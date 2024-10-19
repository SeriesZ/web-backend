from sqlalchemy import update

from database import AsyncSessionLocal
from model.ideation import Ideation


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
