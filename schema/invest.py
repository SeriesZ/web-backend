from typing import Optional

from pydantic import BaseModel


class InvestorRequest(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    image: str
    assets_under_management: str
    investment_count: int

    class Config:
        from_attributes = True


class InvestorResponse(BaseModel):
    name: str
    description: str
    image: str
    assets_under_management: str
    investment_count: int

    class Config:
        from_attributes = True


class InvestmentRequest(BaseModel):
    ideation_id: int
    investor_id: int
    amount: int
    approval_status: bool

    class Config:
        from_attributes = True


class InvestmentResponse(BaseModel):
    ideation_id: str
    investor: InvestorResponse

    amount: int
    approval_status: bool

    class Config:
        from_attributes = True
