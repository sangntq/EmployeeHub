"""
承認履歴モデル（監査ログ）

entity_type: 'employee_skill' | 'employee_certification'
"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ApprovalHistory(Base):
    __tablename__ = "approval_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(
        Enum("SUBMITTED", "APPROVED", "REJECTED", "RESUBMITTED", name="approval_action"),
        nullable=False,
    )
    actor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    actor: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[actor_id])


from app.models.employee import Employee  # noqa: E402
