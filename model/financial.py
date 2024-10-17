from sqlalchemy import JSON, Column, Float, String

from database import Base


class Financial(Base):
    __tablename__ = "financials"

    ideation_id = Column(String, nullable=False)  # 아이디어 ID

    # 원가 항목
    direct_material = Column(Float)  # 직접재료비
    direct_expense = Column(Float)  # 직접경비
    item_input = Column(Float)  # 항목입력
    direct_labor = Column(Float)  # 직접노무비
    manufacturing_cost = Column(Float)  # 제조간접비
    profit_rate = Column(Float)  # 이익률
    sale_price = Column(Float)  # 판매가격 (소비자가격)

    # 판관비 항목
    salary = Column(Float)  # 급여
    office_rent = Column(Float)  # 사무실 임차료
    ad_cost = Column(Float)  # 광고선전비
    business_expense = Column(Float)  # 업무추진비
    maintenance_cost = Column(Float)  # 접대비
    contingency = Column(Float)  # 예비비용
    total_expense = Column(Float)  # 판관비 계 (연비용)

    # 인상율 항목
    salary_increase_rate = Column(Float)  # 급여 인상율
    office_rent_increase_rate = Column(Float)  # 사무실 임차료 인상율
    ad_cost_increase_rate = Column(Float)  # 광고선전비 인상율
    business_expense_increase_rate = Column(Float)  # 업무추진비 인상율
    maintenance_cost_increase_rate = Column(Float)  # 접대비 인상율
    contingency_increase_rate = Column(Float)  # 예비비 인상율

    # 연차별 거래발생 수 및 직원 수
    trade_counts = Column(JSON)  # 거래발생 수 (연차별 리스트)
    employee_counts = Column(JSON)  # 직원 수 (연차별 리스트)
