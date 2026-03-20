"""資格マトリクススキーマ"""
from pydantic import BaseModel
from app.schemas.employee import EmployeeListItem


class CertInfo(BaseModel):
    id: str
    name: str


class EngineerCertEntry(BaseModel):
    cert_id: str
    obtained_at: str | None = None
    expires_at: str | None = None
    expiry_status: str | None = None  # SOON / VALID / NO_EXPIRY


class CertMatrixCategory(BaseModel):
    category: str          # LANGUAGE / CLOUD / PM / NETWORK / SECURITY / OTHER
    certifications: list[CertInfo]


class CertEngineerRow(BaseModel):
    employee: EmployeeListItem
    certs: dict[str, EngineerCertEntry]   # cert_master_id -> entry


class CertMatrixResponse(BaseModel):
    categories: list[CertMatrixCategory]
    engineers: list[CertEngineerRow]
