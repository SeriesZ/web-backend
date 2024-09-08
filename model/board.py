from sqlalchemy import Column, Integer, String

from database import Base


# 공지사항
class Board(Base):
    __tablename__ = "boards"

    title = Column(String, index=True)
    description = Column(String, index=True)
