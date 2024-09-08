from sqlalchemy import Column, Integer, String, Boolean

from auth import get_password_hash, verify_password
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    _password = Column("password", String)
    email = Column(String, index=True, unique=True)
    disabled = Column(Boolean, index=True)

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, plain_password: str):
        self._password = get_password_hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self._password)
