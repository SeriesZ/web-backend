from pydantic import BaseModel


class InvestorResponse(BaseModel):
    name: str
    description: str
    image: str
    assets_under_management: str
    investment_count: int


class ProgressResponse(BaseModel):
    ideation_id: int
    investor: InvestorResponse

    amount: int
    approval_status: bool
