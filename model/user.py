import enum

from sqlalchemy import JSON, Column, String, Enum
from sqlalchemy.orm import relationship

from database import Base
from utils.auth import get_password_hash, verify_password


class RoleEnum(enum.Enum):
    USER = "유저"
    INVESTOR = "투자자"
    LAWYER = "변호사"
    ACCOUNTANT = "회계사"
    TAX_ADVISOR = "세무사"
    ADMIN = "관리자"


class User(Base):
    __tablename__ = "users"

    name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    _password = Column("password", String)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER)
    expertises = Column(JSON, nullable=True)

    group_id = Column(String, nullable=True)

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, plain_password: str):
        self._password = get_password_hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self._password)


class Group(Base):
    __tablename__ = "groups"

    name = Column(String)
    description = Column(String)
    image = Column(String)

    users = relationship(
        "User", primaryjoin="Group.id == foreign(User.group_id)", lazy="joined"
    )
