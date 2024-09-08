from pydantic import BaseModel


class BoardRequest(BaseModel):
    title: str
    description: str = None


class BoardResponse(BaseModel):
    id: int
    title: str
    description: str = None

    class Config:
        from_attributes = True
