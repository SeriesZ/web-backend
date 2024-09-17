from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from database import Base


# 투자회사
class Investors(Base):
    __tablename__ = "investors"

    name = Column(String, unique=True)  # 회사명
    description = Column(String)  # 설명
    image = Column(String)  # 기업 CI 이미지 url
    assets_under_management = Column(String)  # 운용 펀드 금액
    investment_count = Column(Integer)  # 투자 횟수


class Progress(Base):
    __tablename__ = "progress"
    ideation_id = Column(Integer)  # 연결된 id
    investor_id = Column(Integer)  # 투자자 id

    ideation = relationship(
        "Ideation",
        primaryjoin="Progress.ideation_id == Ideation.id",
        foreign_keys="[Progress.ideation_id]",
        lazy="joined",
    )
    investor = relationship(
        "Investors",
        primaryjoin="Progress.investor_id == Investors.id",
        foreign_keys="[Progress.investor_id]",
        lazy="joined",
    )

    amount = Column(Integer)  # 투자 금액
    approval_status = Column(Boolean)  # 투자 승인 여부
