from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship

from database import Base


# 아이디어
class Ideation(Base):
    __tablename__ = "ideations"

    title = Column(String)  # 제목
    description = Column(String)  # 설명
    image = Column(String)  # 대표이미지 url
    theme = Column(String)  # 테마
    close_date = Column(DateTime)  # 라운드 종료 날짜

    user = relationship("User", back_populates="ideations")  # N:1
    comments = relationship("Comment", back_populates="ideation")  # 1:N

    view_count = Column(Integer, default=0)  # 조회수
    progress_rate = Column(Float)  # 달성률

