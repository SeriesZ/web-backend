from pydantic import BaseModel


class BoardRequest(BaseModel):
    category: str
    title: str
    content: str


class BoardResponse(BaseModel):
    id: str
    category: str
    title: str
    content: str

    class Config:
        from_attributes = True
