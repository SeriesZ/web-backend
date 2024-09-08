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

    ideation = relationship("Ideation", back_populates="progress")  # 1:1
    investor = relationship("Investors", back_populates="progress")  # 1:1

    amount = Column(Integer)  # 투자 금액
    approval_status = Column(Boolean)  # 투자 승인 여부
