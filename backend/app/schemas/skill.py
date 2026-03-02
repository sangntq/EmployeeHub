"""スキル関連スキーマ"""
from datetime import date, datetime
from pydantic import BaseModel, field_validator


class SkillResponse(BaseModel):
    id: str
    name: str
    name_ja: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class SkillCategoryResponse(BaseModel):
    id: str
    name_ja: str
    name_en: str
    sort_order: int
    skills: list[SkillResponse] = []

    model_config = {"from_attributes": True}


class SkillMasterListResponse(BaseModel):
    categories: list[SkillCategoryResponse]


class EmployeeSkillCreate(BaseModel):
    skill_id: str
    self_level: int
    experience_years: float | None = None
    last_used_at: date | None = None
    self_comment: str | None = None

    @field_validator("self_level")
    @classmethod
    def validate_level(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("self_level は 1〜5 の整数である必要があります")
        return v


class ApproveSkillRequest(BaseModel):
    approved_level: int
    approver_comment: str | None = None

    @field_validator("approved_level")
    @classmethod
    def validate_level(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("approved_level は 1〜5 の整数である必要があります")
        return v


class RejectSkillRequest(BaseModel):
    approver_comment: str


class EmployeeSkillResponse(BaseModel):
    id: str
    skill: SkillResponse
    self_level: int
    approved_level: int | None = None
    experience_years: float | None = None
    last_used_at: date | None = None
    status: str
    evidence_file_url: str | None = None
    self_comment: str | None = None
    approver_comment: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PendingSkillItem(BaseModel):
    """承認キュー用: スキル申請アイテム"""
    id: str
    employee_id: str
    employee_name_ja: str
    employee_number: str
    skill_name: str
    self_level: int
    experience_years: float | None = None
    evidence_file_url: str | None = None
    self_comment: str | None = None
    submitted_at: datetime
