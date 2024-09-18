from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from model.board import Board
from model.user import User
from schema.board import BoardRequest, BoardResponse

router = APIRouter(tags=["공지사항/게시판"])


@router.post("/boards/", response_model=BoardResponse)
async def create_board(
    board: BoardRequest, db: AsyncSession = Depends(get_db)
):
    db_board = Board(title=board.title, description=board.description)
    db.add(db_board)
    await db.commit()
    await db.refresh(db_board)
    return db_board


@router.get("/boards/", response_model=List[BoardResponse])
async def read_boards(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    boards = await db.execute(select(Board).offset(offset).limit(limit))
    return boards.scalars().all()
