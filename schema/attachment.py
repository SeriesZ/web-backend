from typing import Optional

from pydantic import BaseModel

from schema.user import UserResponse


class AttachmentRequest(BaseModel):
    related_id: str
    file_name: str
    file_path: str


class AttachmentResponse(BaseModel):
    id: str
    related_id: str
    file_name: str
    file_path: str

    class Config:
        from_attributes = True


class CommentRequest(BaseModel):
    related_id: str
    content: str
    rating: Optional[int] = None


class CommentResponse(BaseModel):
    id: str
    related_id: str
    content: str
    rating: Optional[int] = None
    user: UserResponse

    class Config:
        from_attributes = True
