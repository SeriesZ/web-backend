from typing import Union

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserToken(BaseModel):
    id: str
    name: str
    email: str
    role: str
    group_id: Union[str, None] = None
