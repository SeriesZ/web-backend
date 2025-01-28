from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from model.ideation import Status
from schema.attachment import AttachmentResponse, CommentResponse
from schema.invest import InvestmentResponse


class ThemeResponse(BaseModel):
    id: str
    name: str
    image: str
    description: Optional[str] = None
    psr_value: Optional[float] = None

    class Config:
        from_attributes = True


class IdeationRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    theme_id: Optional[str] = None
    presentation_url: Optional[str] = None
    presentation_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    status: Optional[Status] = None


class IdeationResponse(BaseModel):
    id: str
    title: str
    content: str
    theme: ThemeResponse = Field(None, description="업종")
    presentation_url: Optional[str] = None
    presentation_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    status: Optional[str] = None
    view_count: int

    investment_goal: Optional[int] = Field(None, description="목표 금액 (단위: 만원)")
    investments: Optional[List[InvestmentResponse]] = Field(None, description="투자 진행 상황")

    images: Optional[List[AttachmentResponse]] = Field(None, description="이미지 목록")
    attachments: Optional[List[AttachmentResponse]] = Field(None, description="첨부파일 목록")
    comments: Optional[List[CommentResponse]] = Field(None, description="댓글 목록")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
