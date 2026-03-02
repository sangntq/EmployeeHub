"""
資格関連モデル

- CertificationMaster: 資格マスタ
- EmployeeCertification: 個人資格（承認フロー付き）
"""
from datetime import date, datetime
from sqlalchemy import String, Boolean, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class CertificationMaster(Base):
    __tablename__ = "certification_masters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(
        Enum("LANGUAGE", "CLOUD", "PM", "NETWORK", "SECURITY", "OTHER", name="cert_category"),
        nullable=False,
    )
    issuer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    has_expiry: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    employee_certifications: Mapped[list["EmployeeCertification"]] = relationship(
        "EmployeeCertification", back_populates="certification_master"
    )


class EmployeeCertification(Base):
    __tablename__ = "employee_certifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    certification_master_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("certification_masters.id"), nullable=True
    )
    custom_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    score: Mapped[str | None] = mapped_column(String(50), nullable=True)
    obtained_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("PENDING", "APPROVED", "REJECTED", name="approval_status"),
        nullable=False,
        default="PENDING",
    )
    approver_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("employees.id"), nullable=True)
    approver_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    certification_master: Mapped["CertificationMaster | None"] = relationship(
        "CertificationMaster", back_populates="employee_certifications", lazy="selectin"
    )
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id], back_populates="certifications")
    approver: Mapped["Employee | None"] = relationship("Employee", foreign_keys=[approver_id])


from app.models.employee import Employee  # noqa: E402
