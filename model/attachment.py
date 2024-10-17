from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    file_name = Column(String, nullable=False)  # 파일 이름
    file_path = Column(String, nullable=False)  # 파일 경로 (s3 저장 경로)
    related_id = Column(String, nullable=False)  # 연결된 id


class Comment(Base):
    __tablename__ = "comments"

    related_id = Column(String, nullable=False)  # 연결된 id
    content = Column(String, nullable=False)  # 내용
    rating = Column(Integer, nullable=True)  # 별점 (1~5)

    user_id = Column(String, nullable=False)  # 작성자 id
    user = relationship(
        "User",
        primaryjoin="User.id == Comment.user_id",
        foreign_keys="[Comment.user_id]",
        lazy="joined",
    )
