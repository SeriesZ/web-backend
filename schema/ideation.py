from pydantic import BaseModel

from schema.user import UserResponse


class IdeationRequest(BaseModel):
    id: str
    title: str
    content: str
    image: str
    theme: str
    presentation_date: str
    close_date: str
    status: str
    user_id: int


class IdeationResponse(BaseModel):
    id: str
    title: str
    content: str
    image: str
    theme: str
    presentation_date: str
    close_date: str
    status: str
    user: UserResponse
    view_count: int
