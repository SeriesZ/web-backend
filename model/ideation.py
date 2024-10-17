import enum

from sqlalchemy import Column, DateTime, Integer, String, Enum
from sqlalchemy.orm import relationship

from database import Base


class Status(enum.Enum):
    BEFORE_START = "시작전"
    IN_PROGRESS = "진행중"
    END = "종료"


# 아이디어 테마
class Theme(Base):
    __tablename__ = "themes"

    name = Column(String)
    description = Column(String)
    image = Column(String)


# 아이디어
class Ideation(Base):
    __tablename__ = "ideations"

    title = Column(String)  # 제목
    content = Column(String)  # 아이디어 설명
    image = Column(String)  # 대표이미지 url
    presentation_url = Column(String)  # 사업설명회 url
    presentation_date = Column(DateTime(timezone=True))  # 사업설명회 날짜
    close_date = Column(DateTime)  # 라운드 종료 날짜
    status = Column(Enum(Status), default=Status.BEFORE_START)  # 상태 (예: 진행중, 종료)
    view_count = Column(Integer, default=0)  # 조회수

    theme_id = Column(String)  # 테마
    theme = relationship(
        "Theme",
        primaryjoin="Theme.id == Ideation.theme_id",
        foreign_keys="[Ideation.theme_id]",
        lazy="joined",
    )

    user_id = Column(String)  # 대표자 id
    user = relationship(
        "User",
        primaryjoin="User.id == Ideation.user_id",
        foreign_keys="[Ideation.user_id]",
        lazy="joined",
    )

    # 120명 / 30,000,000원 확보 / 달성률 85%
    investments = relationship(
        "Investment",
        back_populates="ideation",
        primaryjoin="Ideation.id == foreign(Investment.ideation_id)",
        lazy="joined",
    )
    investment_goal = Column(Integer)  # 목표 금액 (단위: 만원)
    # 지분율 40%, 액면가 1,000원, 최소 투자금액 1,000원,
    # 최대 투자금액 2,000,000,000원
    investment_terms = Column(String)
