import enum

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from auth import get_password_hash, verify_password
from database import Base


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
    email = Column(String, index=True)
    _password = Column("password", String)
    role = Column(String, default=RoleEnum.USER.value)
    investor_id = Column(String, nullable=True)

    investor = relationship(
        "Investor",
        primaryjoin="User.investor_id == Investor.id",
        foreign_keys="[User.investor_id]",
        lazy="joined",
    )

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, plain_password: str):
        self._password = get_password_hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self._password)
