from sqlalchemy import Column, String

from database import Base


# 공지사항
class Board(Base):
    __tablename__ = "boards"

    category = Column(String)  # 카테고리 [공지사항,이벤트,보도자료,매거진]
    title = Column(String)  # 제목
    description = Column(String)  # 내용
