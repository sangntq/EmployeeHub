"""Phase 1: users / departments / employees テーブル作成 + 管理者シードデータ

Revision ID: 001
Revises:
Create Date: 2026-02-28
"""
from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext
import uuid
from datetime import datetime, date

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade() -> None:
    # ── ENUM 型定義（op.create_table が自動的に CREATE TYPE を発行する）────────
    system_role = sa.Enum(
        "member", "manager", "department_head", "sales", "director", "admin",
        name="system_role",
    )
    employment_type = sa.Enum("FULLTIME", "CONTRACT", "FREELANCE", name="employment_type")
    work_style = sa.Enum("ONSITE", "REMOTE", "HYBRID", name="work_style")
    office_location = sa.Enum("HANOI", "HCMC", "TOKYO", "OSAKA", "OTHER", name="office_location")

    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("google_id", sa.String(255), nullable=True, unique=True),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_google_id", "users", ["google_id"])

    # ── departments ────────────────────────────────────────────────────────
    op.create_table(
        "departments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name_ja", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=True),
        sa.Column("name_vi", sa.String(100), nullable=True),
        sa.Column("parent_id", sa.String(36), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("manager_id", sa.String(36), nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, default=0),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── employees ──────────────────────────────────────────────────────────
    op.create_table(
        "employees",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True),
        sa.Column("employee_number", sa.String(20), nullable=False, unique=True),
        sa.Column("name_ja", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=True),
        sa.Column("name_vi", sa.String(100), nullable=True),
        sa.Column("department_id", sa.String(36), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("system_role", system_role, nullable=False),
        sa.Column("office_location", office_location, nullable=False),
        sa.Column("employment_type", employment_type, nullable=False),
        sa.Column("work_style", work_style, nullable=False),
        sa.Column("joined_at", sa.Date, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("slack_id", sa.String(100), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_employees_employee_number", "employees", ["employee_number"])
    op.create_index("ix_employees_email", "employees", ["email"])

    # ── Seed: 管理者アカウント ──────────────────────────────────────────────
    now = datetime.utcnow()
    admin_user_id = str(uuid.uuid4())
    admin_employee_id = str(uuid.uuid4())

    op.bulk_insert(
        sa.table("users",
            sa.column("id", sa.String),
            sa.column("email", sa.String),
            sa.column("password_hash", sa.String),
            sa.column("is_active", sa.Boolean),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [
            {
                "id": admin_user_id,
                "email": "admin@employeehub.local",
                "password_hash": pwd_context.hash("Admin1234!"),
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    op.bulk_insert(
        sa.table("employees",
            sa.column("id", sa.String),
            sa.column("user_id", sa.String),
            sa.column("employee_number", sa.String),
            sa.column("name_ja", sa.String),
            sa.column("name_en", sa.String),
            sa.column("system_role", sa.String),
            sa.column("office_location", sa.String),
            sa.column("employment_type", sa.String),
            sa.column("work_style", sa.String),
            sa.column("joined_at", sa.Date),
            sa.column("email", sa.String),
            sa.column("is_active", sa.Boolean),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [
            {
                "id": admin_employee_id,
                "user_id": admin_user_id,
                "employee_number": "ADMIN-001",
                "name_ja": "システム管理者",
                "name_en": "System Admin",
                "system_role": "admin",
                "office_location": "HANOI",
                "employment_type": "FULLTIME",
                "work_style": "REMOTE",
                "joined_at": date(2024, 1, 1),
                "email": "admin@employeehub.local",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("employees")
    op.drop_table("departments")
    op.drop_table("users")
    for enum_name in ["system_role", "employment_type", "work_style", "office_location"]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
