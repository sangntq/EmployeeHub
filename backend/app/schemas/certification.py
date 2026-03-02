"""資格関連スキーマ"""
from datetime import date, datetime
from pydantic import BaseModel


class CertificationMasterResponse(BaseModel):
    id: str
    name: str
    category: str
    issuer: str | None = None
    has_expiry: bool

    model_config = {"from_attributes": True}


class EmployeeCertCreate(BaseModel):
    certification_master_id: str | None = None
    custom_name: str | None = None          # マスタにない資格は自由入力
    score: str | None = None
    obtained_at: date
    expires_at: date | None = None
    file_url: str | None = None

    def model_post_init(self, __context) -> None:
        if not self.certification_master_id and not self.custom_name:
            raise ValueError("certification_master_id か custom_name のいずれかは必須です")


class ApproveCertRequest(BaseModel):
    approver_comment: str | None = None


class RejectCertRequest(BaseModel):
    approver_comment: str


class EmployeeCertResponse(BaseModel):
    id: str
    certification_master: CertificationMasterResponse | None = None
    custom_name: str | None = None
    score: str | None = None
    obtained_at: date
    expires_at: date | None = None
    file_url: str | None = None
    status: str
    approver_comment: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PendingCertItem(BaseModel):
    """承認キュー用: 資格申請アイテム"""
    id: str
    employee_id: str
    employee_name_ja: str
    employee_number: str
    cert_name: str
    obtained_at: date
    expires_at: date | None = None
    score: str | None = None
    file_url: str | None = None
    submitted_at: datetime


class PendingApprovalsResponse(BaseModel):
    skills: list["PendingSkillItem"]
    certifications: list[PendingCertItem]


from app.schemas.skill import PendingSkillItem  # noqa: E402
PendingApprovalsResponse.model_rebuild()
