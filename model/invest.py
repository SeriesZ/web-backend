from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# 투자회사
class Investor(Base):
    __tablename__ = "investors"

    name = Column(String)  # 회사명
    description = Column(String)  # 설명
    image = Column(String)  # 기업 CI 이미지 url
    assets_under_management = Column(String)  # 운용 펀드 금액
    investment_count = Column(Integer)  # 투자 횟수


class Investment(Base):
    __tablename__ = "investments"
    ideation_id = Column(Integer)  # 연결된 id
    investor_id = Column(Integer)  # 투자자 id
    amount = Column(Integer)  # 투자 금액
    approval_status = Column(Boolean)  # 투자 승인 여부

    ideation = relationship(
        "Ideation",
        primaryjoin="Investment.ideation_id == Ideation.id",
        foreign_keys="[Investment.ideation_id]",
        lazy="joined",
    )
    investor = relationship(
        "Investor",
        primaryjoin="Investment.investor_id == Investor.id",
        foreign_keys="[Investment.investor_id]",
        lazy="joined",
    )


# 사용자와 투자자의 관계
# class InvestorUser(Base):
#     __tablename__ = 'investor_user'
#
#     user_id = Column(Integer, primary_key=True)
#     investor_id = Column(Integer, primary_key=True)
#
#     # 사용자와 투자자에 대한 관계 설정
#     user = relationship(
#         "User",
#         primaryjoin="User.id == InvestorUser.user_id",
#         foreign_keys="[InvestorUser.user_id]",
#         lazy="joined",
#     )
#     investor = relationship(
#         "Investor",
#         primaryjoin="Investor.id == InvestorUser.investor_id",
#         foreign_keys="[InvestorUser.investor_id]",
#         lazy="joined",
#     )
