from typing import Optional

from pydantic import BaseModel


class UserRequest(BaseModel):
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    group_id: Optional[str] = None

    class Config:
        from_attributes = True
