from datetime import date
from pydantic import BaseModel
from app.schemas.department import DepartmentResponse


class WorkStatusEmbed(BaseModel):
    status: str
    free_from: date | None = None
    note: str | None = None

    model_config = {"from_attributes": True}


class EmployeeCreate(BaseModel):
    employee_number: str
    name_ja: str
    name_en: str | None = None
    name_vi: str | None = None
    email: str  # EmailStr は .local ドメインを拒否するため str を使用
    department_id: str | None = None
    system_role: str = "member"
    office_location: str
    employment_type: str = "FULLTIME"
    work_style: str = "ONSITE"
    joined_at: date
    phone: str | None = None
    slack_id: str | None = None
    japanese_level: str | None = None


class EmployeeUpdate(BaseModel):
    name_ja: str | None = None
    name_en: str | None = None
    name_vi: str | None = None
    email: str | None = None  # EmailStr は .local ドメインを拒否するため str を使用
    department_id: str | None = None
    system_role: str | None = None
    office_location: str | None = None
    employment_type: str | None = None
    work_style: str | None = None
    joined_at: date | None = None
    phone: str | None = None
    slack_id: str | None = None
    japanese_level: str | None = None
    is_active: bool | None = None
    left_at: date | None = None


class EmployeeListItem(BaseModel):
    id: str
    employee_number: str
    name_ja: str
    name_en: str | None = None
    name_vi: str | None = None
    department: DepartmentResponse | None = None
    system_role: str
    office_location: str
    employment_type: str
    work_style: str
    is_active: bool
    avatar_url: str | None = None
    japanese_level: str | None = None
    workload_percent: int | None = None
    is_mobilizable: bool = False

    model_config = {"from_attributes": True}


class EmployeeDetail(EmployeeListItem):
    email: str
    phone: str | None = None
    slack_id: str | None = None
    joined_at: date
    left_at: date | None = None
    user_id: str | None = None


class PaginatedEmployees(BaseModel):
    items: list[EmployeeListItem]
    total: int
    page: int
    per_page: int
