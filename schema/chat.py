from typing import List

from pydantic import BaseModel

from schema.user import UserResponse


class ChatResponse(BaseModel):
    id: str
    users: List[UserResponse]
