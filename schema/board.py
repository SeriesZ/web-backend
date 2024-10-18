from pydantic import BaseModel

from model.board import BoardCategory


class BoardRequest(BaseModel):
    category: BoardCategory
    title: str
    content: str


class BoardResponse(BaseModel):
    id: str
    category: BoardCategory
    title: str
    content: str

    class Config:
        from_attributes = True
