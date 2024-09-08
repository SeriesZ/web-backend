from sqlalchemy import Column, Integer, String

from database import Base


# 투자회사
class Investors(Base):
    __tablename__ = "investors"

    name = Column(String, unique=True)  # 회사명
    description = Column(String)  # 설명
    image = Column(String)  # 기업 CI 이미지 url
    assets_under_management = Column(String)  # 운용 펀드 금액
    investment_count = Column(Integer)  # 투자 횟수
