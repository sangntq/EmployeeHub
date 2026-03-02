"""
稼働状況・アサイン関連モデル

- WorkStatus: 稼働状況（1人1レコード）
- Assignment: アサイン管理
"""
import uuid
from datetime import date, datetime
from sqlalchemy import String, SmallInteger, Boolean, Text, Date, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

WorkStatusEnum = Enum(
    "ASSIGNED", "FREE_IMMEDIATE", "FREE_PLANNED", "INTERNAL", "LEAVE", "LEAVING",
    name="work_status",
)


class WorkStatus(Base):
    __tablename__ = "work_statuses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(WorkStatusEnum, nullable=False, default="FREE_IMMEDIATE")
    free_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    updater: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[updated_by])


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    allocation_percent: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=100)
    started_at: Mapped[date] = mapped_column(Date, nullable=False)
    ends_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    project: Mapped["Project"] = relationship("Project", back_populates="assignments")
    creator: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[created_by])


# 循環インポート回避
from app.models.employee import Employee  # noqa: E402
from app.models.project import Project  # noqa: E402
