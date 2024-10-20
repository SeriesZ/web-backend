from sqlalchemy import Column, String
from sqlalchemy.orm import backref, relationship

from database import Base


class ChatUser(Base):
    __tablename__ = "chat_user"

    chat_id = Column(String)
    user_id = Column(String)


class Chat(Base):
    __tablename__ = "chat"

    users = relationship(
        "User",
        secondary=ChatUser.__table__,
        primaryjoin="foreign(ChatUser.chat_id) == Chat.id",
        secondaryjoin="foreign(ChatUser.user_id) == User.id",
        lazy="subquery",
        backref=backref("chat_user", lazy=True),
    )
