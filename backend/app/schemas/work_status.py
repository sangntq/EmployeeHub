"""
稼働状況・アサイン関連 Pydantic スキーマ
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkStatusResponse(BaseModel):
    id: str
    employee_id: str
    status: str
    free_from: Optional[date] = None
    note: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkStatusUpdate(BaseModel):
    status: str = Field(..., description="稼働ステータス")
    free_from: Optional[date] = Field(None, description="フリー予定日（FREE_PLANNEDの場合）")
    note: Optional[str] = Field(None, description="備考")


class AssignmentCreate(BaseModel):
    project_id: str
    allocation_percent: int = Field(100, ge=1, le=100)
    started_at: date
    ends_at: Optional[date] = None


class AssignmentResponse(BaseModel):
    id: str
    employee_id: str
    project_id: str
    project_name: Optional[str] = None
    allocation_percent: int
    started_at: date
    ends_at: Optional[date] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AssignmentUpdate(BaseModel):
    allocation_percent: Optional[int] = Field(None, ge=1, le=100)
    ends_at: Optional[date] = None
    is_active: Optional[bool] = None
