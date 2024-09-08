from typing import Union

from pydantic import BaseModel


class UserRequest(BaseModel):
    name: str
    password: str
    email: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: Union[str, None] = None

    class Config:
        from_attributes = True
