from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# 아이디어
class Ideation(Base):
    __tablename__ = "ideations"

    title = Column(String)  # 제목
    content = Column(String)  # 아이디어 설명
    image = Column(String)  # 대표이미지 url
    theme = Column(String)  # 테마
    presentation_date = Column(DateTime(timezone=True))  # 사업설명회 날짜
    close_date = Column(DateTime)  # 라운드 종료 날짜
    status = Column(String)  # 상태 (예: 진행중, 종료)
    user_id = Column(Integer)  # 작성자 id

    user = relationship(
        "User",
        primaryjoin="User.id == Ideation.user_id",
        foreign_keys="[Ideation.user_id]",
        lazy="joined",
    )

    # TODO comments, attachments 따로 병렬로 불러오는 방식으로 변경
    # comments = relationship(
    #     "Comment",
    #     primaryjoin="Comment.related_id == Ideation.id",
    #     foreign_keys="[Comment.related_id]",
    #     lazy="joined",
    # )
    #
    # attachments = relationship(
    #     "Attachment",
    #     primaryjoin="Attachment.related_id == Ideation.id",
    #     foreign_keys="[Attachment.related_id]",
    #     lazy="joined",
    # )

    view_count = Column(Integer, default=0)  # 조회수

    # TODO
    # progress = relationship("Progress", back_populates="ideation")
    # 120명 / 30,000,000원 확보 / 달성률 85%

    # FIXME 투자 조건 (text or html)
    # 아래 외의 투자조건이 다양하게 있으면 text로 저장하는게 편리.
    # 정해진 category 있으면 테이블로 분리.
    # progress에 저장되는 투자금액 / 지분율 과 dependency 있음.
    # https://docs.google.com/presentation/d/1pl8XtREE02ronq4xY5C9tSwUhBDwLKKh/edit#slide=id.p144

    # 지분율 40%, 액면가 1,000원, 최소 투자금액 1,000원,
    # 최대 투자금액 2,000,000,000원
    investment_terms = Column(String)
