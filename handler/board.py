from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from auth import get_current_user
from database import get_db
from model.board import Board
from model.user import RoleEnum, User
from schema.board import BoardRequest, BoardResponse

router = APIRouter(tags=["공지사항/게시판"])


@router.get("/boards/", response_model=List[BoardResponse])
async def read_boards(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    boards = await db.execute(select(Board).offset(offset).limit(limit))
    boards = boards.scalars().all()
    return [BoardResponse.model_validate(b) for b in boards]


@router.get("/board/{id}", response_model=BoardResponse)
async def read_board(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    board = await db.execute(select(Board).where(Board.id == id))
    board = board.scalars().first()
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return BoardResponse.model_validate(board)


@router.post("/board/", status_code=201)
async def create_board(
    board: BoardRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")

    board = Board(
        category=board.category,
        title=board.title,
        content=board.content,
    )
    db.add(board)


@router.put("/board/{id}", status_code=200)
async def update_board(
    id: str,
    board: BoardRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(
        update(Board)
        .where(Board.id == id)
        .values(**board.dict(exclude_unset=True))
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Board not found")


@router.delete("/board/{id}", status_code=204)
async def delete_board(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")

    result = await db.execute(delete(Board).where(Board.id == id))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Board not found")
