"""稼働可否スケジュールスキーマ"""
from pydantic import BaseModel
from app.schemas.employee import EmployeeListItem


class AvailabilityMonth(BaseModel):
    month: str       # "2026-03"
    status: str      # FREE | PARTIAL | BUSY
    allocation: int
    project_name: str | None = None


class EmployeeAvailability(BaseModel):
    employee: EmployeeListItem
    months: list[AvailabilityMonth]


class AvailabilityResponse(BaseModel):
    months_header: list[str]
    items: list[EmployeeAvailability]
