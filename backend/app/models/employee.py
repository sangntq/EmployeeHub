import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

# PostgreSQL ENUM 型定義
SystemRoleEnum = SAEnum(
    "member", "manager", "department_head", "sales", "director", "admin",
    name="system_role", create_type=True,
)
EmploymentTypeEnum = SAEnum("FULLTIME", "CONTRACT", "FREELANCE", name="employment_type", create_type=True)
WorkStyleEnum = SAEnum("ONSITE", "REMOTE", "HYBRID", name="work_style", create_type=True)
OfficeLocationEnum = SAEnum("HANOI", "HCMC", "TOKYO", "OSAKA", "OTHER", name="office_location", create_type=True)


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    employee_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name_ja: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(100), nullable=True)
    name_vi: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    system_role: Mapped[str] = mapped_column(SystemRoleEnum, nullable=False, default="member")
    office_location: Mapped[str] = mapped_column(OfficeLocationEnum, nullable=False)
    employment_type: Mapped[str] = mapped_column(EmploymentTypeEnum, nullable=False, default="FULLTIME")
    work_style: Mapped[str] = mapped_column(WorkStyleEnum, nullable=False, default="ONSITE")
    joined_at: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    slack_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    japanese_level: Mapped[str | None] = mapped_column(String(10), nullable=True)  # N5/N4/N3/N2/N1/NATIVE/NONE
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    left_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーション
    user: Mapped["User | None"] = relationship("User")  # type: ignore[name-defined]
    department: Mapped["Department | None"] = relationship("Department")  # type: ignore[name-defined]
    skills: Mapped[list["EmployeeSkill"]] = relationship(  # type: ignore[name-defined]
        "EmployeeSkill", foreign_keys="EmployeeSkill.employee_id", back_populates="employee"
    )
    certifications: Mapped[list["EmployeeCertification"]] = relationship(  # type: ignore[name-defined]
        "EmployeeCertification", foreign_keys="EmployeeCertification.employee_id", back_populates="employee"
    )
    work_status: Mapped["WorkStatus | None"] = relationship(  # type: ignore[name-defined]
        "WorkStatus", foreign_keys="WorkStatus.employee_id", back_populates="employee", uselist=False
    )
    projects: Mapped[list["EmployeeProject"]] = relationship(  # type: ignore[name-defined]
        "EmployeeProject", foreign_keys="EmployeeProject.employee_id", back_populates="employee"
    )
    visa_info: Mapped["VisaInfo | None"] = relationship(  # type: ignore[name-defined]
        "VisaInfo", foreign_keys="VisaInfo.employee_id", back_populates="employee", uselist=False
    )
