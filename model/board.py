import enum

from sqlalchemy import Column, String, Enum

from database import Base


class BoardCategory(enum.Enum):
    NOTICE = "공지사항"
    EVENT = "이벤트"
    PRESS_RELEASE = "보도자료"
    MAGAZINE = "매거진"


# 공지사항
class Board(Base):
    __tablename__ = "boards"

    category = Column(Enum(BoardCategory), nullable=False)  # Enum 타입 사용
    title = Column(String, nullable=False)  # 제목
    content = Column(String, nullable=False)  # 내용
