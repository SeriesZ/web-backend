import enum

from sqlalchemy import Column, String

from auth import get_password_hash, verify_password
from database import Base


class RoleEnum(enum.Enum):
    USER = "유저"
    ADMIN = "관리자"
    LAWYER = "변호사"
    ACCOUNTANT = "회계사"
    TAX_ADVISOR = "세무사"


class User(Base):
    __tablename__ = "users"

    name = Column(String, index=True)
    email = Column(String, index=True)
    _password = Column("password", String)

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, plain_password: str):
        self._password = get_password_hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self._password)
