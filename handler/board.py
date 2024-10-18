from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import and_
from starlette.exceptions import HTTPException

from auth import get_current_user
from model.board import Board, BoardCategory
from model.user import RoleEnum, User
from schema.board import BoardRequest, BoardResponse
from service.repository import CrudRepository, get_repository

router = APIRouter(tags=["공지사항/게시판"])


@router.get("/boards", response_model=List[BoardResponse])
async def read_boards(
        category: BoardCategory = None,
        offset: int = 0,
        limit: int = 10,
        repo: CrudRepository = Depends(get_repository),
):
    clause = None
    if category:
        clause = and_(Board.category == category)
    boards = await repo.fetch_all(Board, offset, limit, clause)
    return [BoardResponse.model_validate(b) for b in boards]


@router.get("/board/{id}", response_model=BoardResponse)
async def read_board(
        id: str,
        repo: CrudRepository = Depends(get_repository),
):
    board = await repo.find_by_id(Board, id)
    return BoardResponse.model_validate(board)


@router.post("/board", response_model=BoardResponse)
async def create_board(
        board: BoardRequest,
        repo: CrudRepository = Depends(get_repository),
        current_user: User = Depends(get_current_user),
):
    if not current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")

    board = Board(
        category=board.category,
        title=board.title,
        content=board.content,
    )
    board = await repo.create(board)
    return BoardResponse.model_validate(board)


@router.put("/board/{id}", status_code=200)
async def update_board(
        id: str,
        request: BoardRequest,
        repo: CrudRepository = Depends(get_repository),
        current_user: User = Depends(get_current_user),
):
    if not current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")

    board = Board(id=id, **request.dict())
    board = await repo.update(board)
    return BoardResponse.model_validate(board)


@router.delete("/board/{id}", status_code=204)
async def delete_board(
        id: str,
        repo: CrudRepository = Depends(get_repository),
        current_user: User = Depends(get_current_user),
):
    if not current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")
    await repo.delete(Board(id=id))
