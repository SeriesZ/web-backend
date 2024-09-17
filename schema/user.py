from pydantic import BaseModel

from schema.token import Token


class UserRequest(BaseModel):
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    token: Token

    class Config:
        from_attributes = True
