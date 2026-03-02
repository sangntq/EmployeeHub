"""Phase 3: work_statuses / assignments / projects / employee_projects / visa_info

Revision ID: 003
Revises: 002
Create Date: 2026-03-01
"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    work_status_enum = sa.Enum(
        "ASSIGNED", "FREE_IMMEDIATE", "FREE_PLANNED", "INTERNAL", "LEAVE", "LEAVING",
        name="work_status",
    )
    project_role_enum = sa.Enum(
        "PL", "PM", "SE", "PG", "QA", "INFRA", "DESIGNER", "OTHER",
        name="project_role",
    )

    # ── work_statuses ────────────────────────────────────────────────────────
    op.create_table(
        "work_statuses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "employee_id",
            sa.String(36),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("status", work_status_enum, nullable=False, server_default="FREE_IMMEDIATE"),
        sa.Column("free_from", sa.Date, nullable=True),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("updated_by", sa.String(36), sa.ForeignKey("employees.id"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_work_statuses_status", "work_statuses", ["status"])

    # ── projects（プロジェクトマスタ）─────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("client_name", sa.String(200), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("started_at", sa.Date, nullable=True),
        sa.Column("ended_at", sa.Date, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("employees.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── employee_projects（プロジェクト経歴）────────────────────────────────────
    op.create_table(
        "employee_projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "employee_id",
            sa.String(36),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("role", project_role_enum, nullable=False),
        sa.Column("started_at", sa.Date, nullable=False),
        sa.Column("ended_at", sa.Date, nullable=True),
        sa.Column("tech_stack", sa.JSON, nullable=True),   # list[str]
        sa.Column("team_size", sa.SmallInteger, nullable=True),
        sa.Column("responsibilities", sa.Text, nullable=True),
        sa.Column("achievements", sa.Text, nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_employee_projects_employee", "employee_projects", ["employee_id"])

    # ── assignments（アサイン管理）────────────────────────────────────────────
    op.create_table(
        "assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "employee_id",
            sa.String(36),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("allocation_percent", sa.SmallInteger, nullable=False, server_default="100"),
        sa.Column("started_at", sa.Date, nullable=False),
        sa.Column("ends_at", sa.Date, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("employees.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_assignments_employee", "assignments", ["employee_id"])

    # ── visa_info（ビザ情報）────────────────────────────────────────────────
    op.create_table(
        "visa_info",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "employee_id",
            sa.String(36),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("visa_type", sa.String(100), nullable=True),
        sa.Column("residence_card_number", sa.String(20), nullable=True),
        sa.Column("expires_at", sa.Date, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("updated_by", sa.String(36), sa.ForeignKey("employees.id"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_visa_expires", "visa_info", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_visa_expires", table_name="visa_info")
    op.drop_table("visa_info")
    op.drop_index("ix_assignments_employee", table_name="assignments")
    op.drop_table("assignments")
    op.drop_index("ix_employee_projects_employee", table_name="employee_projects")
    op.drop_table("employee_projects")
    op.drop_table("projects")
    op.drop_index("ix_work_statuses_status", table_name="work_statuses")
    op.drop_table("work_statuses")

    # PostgreSQL ENUM 型を削除
    work_status_enum = sa.Enum(name="work_status")
    work_status_enum.drop(op.get_bind(), checkfirst=True)
    project_role_enum = sa.Enum(name="project_role")
    project_role_enum.drop(op.get_bind(), checkfirst=True)
