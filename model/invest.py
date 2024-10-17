from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# 투자회사
class Investor(Base):
    __tablename__ = "investors"

    name = Column(String)  # 회사명
    description = Column(String)  # 설명
    image = Column(String)  # 기업 CI 이미지 url
    assets_under_management = Column(String)  # 운용 펀드 금액
    investment_count = Column(Integer)  # 투자 횟수


class Investment(Base):
    __tablename__ = "investments"

    ideation_id = Column(String)  # 연결된 id
    ideation = relationship(
        "Ideation",
        primaryjoin="Investment.ideation_id == Ideation.id",
        foreign_keys="[Investment.ideation_id]",
        lazy="joined",
    )
    investor_id = Column(String)  # 투자자 id
    investor = relationship(
        "Investor",
        primaryjoin="Investment.investor_id == Investor.id",
        foreign_keys="[Investment.investor_id]",
        lazy="joined",
    )
    amount = Column(Integer)  # 투자 금액
    approval_status = Column(Boolean)  # 투자 승인 여부
