"""スキルマトリクススキーマ"""
from pydantic import BaseModel
from app.schemas.employee import EmployeeListItem


class SkillInfo(BaseModel):
    id: str
    name: str   # skill.name_ja ?? skill.name


class EngineerSkillEntry(BaseModel):
    skill_id: str
    level: int | None = None
    years: float | None = None


class SkillMatrixCategory(BaseModel):
    id: str
    name_ja: str
    skills: list[SkillInfo]


class EngineerRow(BaseModel):
    employee: EmployeeListItem
    skills: dict[str, EngineerSkillEntry]   # skill_id -> entry


class SkillMatrixResponse(BaseModel):
    categories: list[SkillMatrixCategory]
    engineers: list[EngineerRow]
