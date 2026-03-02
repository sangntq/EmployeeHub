from pydantic import BaseModel


class DepartmentBase(BaseModel):
    name_ja: str
    name_en: str | None = None
    name_vi: str | None = None
    parent_id: str | None = None
    sort_order: int = 0


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name_ja: str | None = None
    name_en: str | None = None
    name_vi: str | None = None
    parent_id: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class DepartmentResponse(DepartmentBase):
    id: str
    is_active: bool

    model_config = {"from_attributes": True}
