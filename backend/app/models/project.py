"""
プロジェクト・ビザ情報関連モデル

- Project: プロジェクトマスタ
- EmployeeProject: プロジェクト経歴
- VisaInfo: ビザ情報（1人1レコード）
"""
import uuid
from datetime import date, datetime
from sqlalchemy import String, SmallInteger, Text, Date, DateTime, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

ProjectRoleEnum = Enum(
    "PL", "PM", "SE", "PG", "QA", "INFRA", "DESIGNER", "OTHER",
    name="project_role",
)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    client_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    ended_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    employee_projects: Mapped[list["EmployeeProject"]] = relationship(
        "EmployeeProject", back_populates="project"
    )
    assignments: Mapped[list["Assignment"]] = relationship("Assignment", back_populates="project")


class EmployeeProject(Base):
    __tablename__ = "employee_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    role: Mapped[str] = mapped_column(ProjectRoleEnum, nullable=False)
    started_at: Mapped[date] = mapped_column(Date, nullable=False)
    ended_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    tech_stack: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)  # list[str] stored as JSON
    team_size: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    achievements: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship("Employee", back_populates="projects")
    project: Mapped["Project"] = relationship("Project", back_populates="employee_projects", lazy="selectin")


class VisaInfo(Base):
    __tablename__ = "visa_info"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    visa_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    residence_card_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    updater: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[updated_by])


# 循環インポート回避
from app.models.employee import Employee  # noqa: E402
from app.models.work_status import Assignment  # noqa: E402
