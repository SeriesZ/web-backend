from sqlalchemy import Column, String

from database import Base


# 시리즈 매거진
class News(Base):
    __tablename__ = "news"

    title = Column(String)  # 제목
    content = Column(String)  # 내용
    image = Column(String)  # 대표이미지 url
