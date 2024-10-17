from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from schema.attachment import AttachmentResponse, CommentResponse
from schema.invest import InvestmentResponse


class ThemeResponse(BaseModel):
    id: str
    name: str
    image: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


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
    theme: ThemeResponse
    presentation_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    status: Optional[str] = None
    view_count: int

    investment_goal: Optional[int] = Field(
        ..., description="목표 금액 (단위: 만원)"
    )
    investments: Optional[List[InvestmentResponse]] = Field(
        ..., description="투자 진행 상황"
    )
    attachments: Optional[List[AttachmentResponse]] = Field(
        None, description="첨부파일 목록"
    )
    comments: Optional[List[CommentResponse]] = Field(
        None, description="댓글 목록"
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
