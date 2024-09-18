from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from schema.invest import ProgressResponse


class IdeationRequest(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    image: str
    theme: str
    presentation_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    status: Optional[str] = None


class IdeationResponse(BaseModel):
    id: str
    title: str
    content: str
    image: str
    theme: str
    presentation_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    status: Optional[str] = None

    view_count: int
    investment_goal: Optional[int] \
        = Field(..., description="목표 금액 (단위: 만원)")
    progress: Optional[List[ProgressResponse]] \
        = Field(..., description="투자 진행 상황")

