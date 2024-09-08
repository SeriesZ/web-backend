from pydantic import BaseModel


class UserRequest(BaseModel):
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    email: str
    name: str

    class Config:
        from_attributes = True
