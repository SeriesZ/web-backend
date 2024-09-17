from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
