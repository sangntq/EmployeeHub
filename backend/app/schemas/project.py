"""
プロジェクト経歴・ビザ情報 Pydantic スキーマ
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class EmployeeProjectCreate(BaseModel):
    project_name: str
    client_name: Optional[str] = None
    industry: Optional[str] = None
    role: str
    started_at: date
    ended_at: Optional[date] = None
    tech_stack: Optional[list[str]] = None
    team_size: Optional[int] = None
    responsibilities: Optional[str] = None
    achievements: Optional[str] = None


class EmployeeProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    industry: Optional[str] = None
    role: Optional[str] = None
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    tech_stack: Optional[list[str]] = None
    team_size: Optional[int] = None
    responsibilities: Optional[str] = None
    achievements: Optional[str] = None


class ProjectInfo(BaseModel):
    id: str
    name: str
    client_name: Optional[str] = None
    industry: Optional[str] = None

    model_config = {"from_attributes": True}


class EmployeeProjectResponse(BaseModel):
    id: str
    employee_id: str
    project_id: str
    project: ProjectInfo
    role: str
    started_at: date
    ended_at: Optional[date] = None
    tech_stack: Optional[list[str]] = None
    team_size: Optional[int] = None
    responsibilities: Optional[str] = None
    achievements: Optional[str] = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectReorderRequest(BaseModel):
    ordered_ids: list[str]


class VisaInfoResponse(BaseModel):
    id: str
    employee_id: str
    visa_type: Optional[str] = None
    residence_card_number: Optional[str] = None
    expires_at: Optional[date] = None
    notes: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class VisaInfoUpdate(BaseModel):
    visa_type: Optional[str] = None
    residence_card_number: Optional[str] = None
    expires_at: Optional[date] = None
    notes: Optional[str] = None
