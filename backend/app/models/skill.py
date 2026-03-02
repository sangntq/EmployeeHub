"""
スキル関連モデル

- SkillCategory: スキルカテゴリマスタ
- Skill: スキルマスタ
- EmployeeSkill: 個人スキル（承認フロー付き）
"""
from datetime import date, datetime
from sqlalchemy import String, Integer, SmallInteger, Boolean, Text, Date, DateTime, Numeric, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name_ja: Mapped[str] = mapped_column(String(50), nullable=False)
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    skills: Mapped[list["Skill"]] = relationship("Skill", back_populates="category", lazy="selectin")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("skill_categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name_ja: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    category: Mapped["SkillCategory"] = relationship("SkillCategory", back_populates="skills")
    employee_skills: Mapped[list["EmployeeSkill"]] = relationship("EmployeeSkill", back_populates="skill")


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    __table_args__ = (
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), nullable=False)
    self_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    approved_level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    experience_years: Mapped[float | None] = mapped_column(Numeric(4, 1), nullable=True)
    last_used_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("PENDING", "APPROVED", "REJECTED", name="approval_status"),
        nullable=False,
        default="PENDING",
    )
    evidence_file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    self_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    approver_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    approver_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    skill: Mapped["Skill"] = relationship("Skill", back_populates="employee_skills", lazy="selectin")
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id], back_populates="skills")
    approver: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[approver_id])


# 循環インポート回避
from app.models.employee import Employee  # noqa: E402
