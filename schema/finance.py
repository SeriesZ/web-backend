from typing import List, Optional

from pydantic import BaseModel


class FinanceScheme(BaseModel):
    ideation_id: str  # 아이디어 ID

    # 원가 항목
    direct_material: Optional[float]  # 직접재료비
    direct_expense: Optional[float]  # 직접경비
    direct_labor: Optional[float]  # 직접노무비
    manufacturing_cost: Optional[float]  # 제조간접비
    profit_rate: Optional[float]  # 이익률
    sale_price: Optional[float]  # 판매가격 (소비자가격)

    # 판관비 항목
    salary: Optional[float]  # 급여
    office_rent: Optional[float]  # 사무실 임차료
    ad_cost: Optional[float]  # 광고선전비
    business_expense: Optional[float]  # 업무추진비
    maintenance_cost: Optional[float]  # 접대비
    contingency: Optional[float]  # 예비비용
    total_expense: Optional[float]  # 판관비 계 (연비용)

    # 인상율 항목
    salary_increase_rate: Optional[float]  # 급여 인상율
    office_rent_increase_rate: Optional[float]  # 사무실 임차료 인상율
    ad_cost_increase_rate: Optional[float]  # 광고선전비 인상율
    business_expense_increase_rate: Optional[float]  # 업무추진비 인상율
    maintenance_cost_increase_rate: Optional[float]  # 접대비 인상율
    contingency_increase_rate: Optional[float]  # 예비비 인상율

    # 연차별 거래발생 수 및 직원 수
    trade_counts: Optional[List[int]]  # 거래발생 수 (연차별 리스트)
    employee_counts: Optional[List[int]]  # 직원 수 (연차별 리스트)

    class Config:
        from_attributes = True


class FinanceRequest(FinanceScheme):
    pass


class FinanceResponse(FinanceScheme):
    id: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
