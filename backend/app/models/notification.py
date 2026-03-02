"""
通知モデル

- Notification: アプリ内通知（1社員複数件）
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

NotificationTypeEnum = Enum(
    "VISA_EXPIRY",
    "CERT_EXPIRY",
    "SKILL_APPROVED",
    "SKILL_REJECTED",
    "CERT_APPROVED",
    "CERT_REJECTED",
    "ASSIGNMENT_ENDING",
    "PROFILE_STALE",
    "APPROVAL_REQUESTED",
    name="notification_type",
)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(NotificationTypeEnum, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    related_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    related_entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    recipient: Mapped["Employee"] = relationship("Employee", foreign_keys=[recipient_id])


# 循環インポート回避
from app.models.employee import Employee  # noqa: E402
