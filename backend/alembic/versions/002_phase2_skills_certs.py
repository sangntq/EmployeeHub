"""Phase 2: skill_categories / skills / employee_skills /
           certification_masters / employee_certifications / approval_history

Revision ID: 002
Revises: 001
Create Date: 2026-03-01
"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── ENUM 型（op.create_table が自動発行するため explicit create 不要）────
    approval_status = sa.Enum("PENDING", "APPROVED", "REJECTED", name="approval_status")
    cert_category = sa.Enum(
        "LANGUAGE", "CLOUD", "PM", "NETWORK", "SECURITY", "OTHER",
        name="cert_category",
    )
    approval_action = sa.Enum(
        "SUBMITTED", "APPROVED", "REJECTED", "RESUBMITTED",
        name="approval_action",
    )

    # ── skill_categories ────────────────────────────────────────────────────
    op.create_table(
        "skill_categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name_ja", sa.String(50), nullable=False),
        sa.Column("name_en", sa.String(50), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, default=0),
    )

    # ── skills ─────────────────────────────────────────────────────────────
    op.create_table(
        "skills",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("skill_categories.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("name_ja", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_skills_category_id", "skills", ["category_id"])

    # ── employee_skills ─────────────────────────────────────────────────────
    op.create_table(
        "employee_skills",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("employee_id", sa.String(36), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.String(36), sa.ForeignKey("skills.id"), nullable=False),
        sa.Column("self_level", sa.SmallInteger, nullable=False),
        sa.Column("approved_level", sa.SmallInteger, nullable=True),
        sa.Column("experience_years", sa.Numeric(4, 1), nullable=True),
        sa.Column("last_used_at", sa.Date, nullable=True),
        sa.Column("status", approval_status, nullable=False, server_default="PENDING"),
        sa.Column("evidence_file_url", sa.String(500), nullable=True),
        sa.Column("self_comment", sa.Text, nullable=True),
        sa.Column("approver_id", sa.String(36), sa.ForeignKey("employees.id"), nullable=True),
        sa.Column("approver_comment", sa.Text, nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )
    op.create_index("ix_employee_skills_employee_id", "employee_skills", ["employee_id"])
    op.create_index("ix_employee_skills_skill_id", "employee_skills", ["skill_id"])
    op.create_index("ix_employee_skills_status", "employee_skills", ["status"])

    # ── certification_masters ───────────────────────────────────────────────
    op.create_table(
        "certification_masters",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", cert_category, nullable=False),
        sa.Column("issuer", sa.String(100), nullable=True),
        sa.Column("has_expiry", sa.Boolean, nullable=False, default=True),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
    )

    # ── employee_certifications ─────────────────────────────────────────────
    op.create_table(
        "employee_certifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("employee_id", sa.String(36), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("certification_master_id", sa.String(36), sa.ForeignKey("certification_masters.id"), nullable=True),
        sa.Column("custom_name", sa.String(200), nullable=True),
        sa.Column("score", sa.String(50), nullable=True),
        sa.Column("obtained_at", sa.Date, nullable=False),
        sa.Column("expires_at", sa.Date, nullable=True),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("status", approval_status, nullable=False, server_default="PENDING"),
        sa.Column("approver_id", sa.String(36), sa.ForeignKey("employees.id"), nullable=True),
        sa.Column("approver_comment", sa.Text, nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_employee_certs_employee_id", "employee_certifications", ["employee_id"])
    op.create_index("ix_employee_certs_expires_at", "employee_certifications", ["expires_at"])
    op.create_index("ix_employee_certs_status", "employee_certifications", ["status"])

    # ── approval_history ────────────────────────────────────────────────────
    op.create_table(
        "approval_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("action", approval_action, nullable=False),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_approval_history_entity", "approval_history", ["entity_type", "entity_id"])

    # ── Seed: スキルカテゴリ ────────────────────────────────────────────────
    now = datetime.utcnow()

    cat_lang_id  = str(uuid.uuid4())
    cat_fw_id    = str(uuid.uuid4())
    cat_db_id    = str(uuid.uuid4())
    cat_cloud_id = str(uuid.uuid4())
    cat_infra_id = str(uuid.uuid4())
    cat_domain_id = str(uuid.uuid4())

    op.bulk_insert(
        sa.table(
            "skill_categories",
            sa.column("id", sa.String),
            sa.column("name_ja", sa.String),
            sa.column("name_en", sa.String),
            sa.column("sort_order", sa.Integer),
        ),
        [
            {"id": cat_lang_id,   "name_ja": "プログラミング言語", "name_en": "Programming Language", "sort_order": 1},
            {"id": cat_fw_id,     "name_ja": "フレームワーク",     "name_en": "Framework",            "sort_order": 2},
            {"id": cat_db_id,     "name_ja": "データベース",       "name_en": "Database",             "sort_order": 3},
            {"id": cat_cloud_id,  "name_ja": "クラウド",          "name_en": "Cloud",                "sort_order": 4},
            {"id": cat_infra_id,  "name_ja": "インフラ・ツール",   "name_en": "Infrastructure/Tools", "sort_order": 5},
            {"id": cat_domain_id, "name_ja": "ドメイン知識",       "name_en": "Domain Knowledge",     "sort_order": 6},
        ],
    )

    # ── Seed: スキルマスタ ─────────────────────────────────────────────────
    skills_seed = [
        # プログラミング言語
        (cat_lang_id,  "Java",       "Java"),
        (cat_lang_id,  "Python",     "Python"),
        (cat_lang_id,  "TypeScript", "TypeScript"),
        (cat_lang_id,  "JavaScript", "JavaScript"),
        (cat_lang_id,  "Go",         "Go"),
        (cat_lang_id,  "Kotlin",     "Kotlin"),
        (cat_lang_id,  "PHP",        "PHP"),
        (cat_lang_id,  "Ruby",       "Ruby"),
        (cat_lang_id,  "C#",         "C#"),
        (cat_lang_id,  "Swift",      "Swift"),
        # フレームワーク
        (cat_fw_id,    "Spring Boot",  "Spring Boot"),
        (cat_fw_id,    "FastAPI",      "FastAPI"),
        (cat_fw_id,    "Django",       "Django"),
        (cat_fw_id,    "React",        "React"),
        (cat_fw_id,    "Vue.js",       "Vue.js"),
        (cat_fw_id,    "Angular",      "Angular"),
        (cat_fw_id,    "Next.js",      "Next.js"),
        (cat_fw_id,    "NestJS",       "NestJS"),
        (cat_fw_id,    "Laravel",      "Laravel"),
        (cat_fw_id,    "Ruby on Rails","Ruby on Rails"),
        # データベース
        (cat_db_id,    "PostgreSQL",   "PostgreSQL"),
        (cat_db_id,    "MySQL",        "MySQL"),
        (cat_db_id,    "MongoDB",      "MongoDB"),
        (cat_db_id,    "Redis",        "Redis"),
        (cat_db_id,    "Elasticsearch","Elasticsearch"),
        (cat_db_id,    "Oracle DB",    "Oracle DB"),
        # クラウド
        (cat_cloud_id, "AWS",          "AWS"),
        (cat_cloud_id, "GCP",          "GCP"),
        (cat_cloud_id, "Azure",        "Azure"),
        (cat_cloud_id, "Cloudflare",   "Cloudflare"),
        # インフラ・ツール
        (cat_infra_id, "Docker",       "Docker"),
        (cat_infra_id, "Kubernetes",   "Kubernetes"),
        (cat_infra_id, "Terraform",    "Terraform"),
        (cat_infra_id, "GitHub Actions","GitHub Actions"),
        (cat_infra_id, "Jenkins",      "Jenkins"),
        (cat_infra_id, "Nginx",        "Nginx"),
        (cat_infra_id, "Linux",        "Linux"),
        # ドメイン知識
        (cat_domain_id, "機械学習",    "Machine Learning"),
        (cat_domain_id, "データ分析",  "Data Analysis"),
        (cat_domain_id, "セキュリティ","Security"),
    ]

    op.bulk_insert(
        sa.table(
            "skills",
            sa.column("id", sa.String),
            sa.column("category_id", sa.String),
            sa.column("name", sa.String),
            sa.column("name_ja", sa.String),
            sa.column("is_active", sa.Boolean),
            sa.column("created_at", sa.DateTime),
        ),
        [
            {
                "id": str(uuid.uuid4()),
                "category_id": cat_id,
                "name": name,
                "name_ja": name_ja,
                "is_active": True,
                "created_at": now,
            }
            for cat_id, name, name_ja in skills_seed
        ],
    )

    # ── Seed: 資格マスタ ────────────────────────────────────────────────────
    cert_masters_seed = [
        ("JLPT N1",                "LANGUAGE", "国際交流基金・日本国際教育支援協会", True),
        ("JLPT N2",                "LANGUAGE", "国際交流基金・日本国際教育支援協会", True),
        ("JLPT N3",                "LANGUAGE", "国際交流基金・日本国際教育支援協会", True),
        ("JLPT N4",                "LANGUAGE", "国際交流基金・日本国際教育支援協会", True),
        ("JLPT N5",                "LANGUAGE", "国際交流基金・日本国際教育支援協会", True),
        ("AWS Certified SAA",      "CLOUD",    "Amazon Web Services",               True),
        ("AWS Certified SAP",      "CLOUD",    "Amazon Web Services",               True),
        ("AWS Certified DVA",      "CLOUD",    "Amazon Web Services",               True),
        ("Google Cloud ACE",       "CLOUD",    "Google",                            True),
        ("Google Cloud PCA",       "CLOUD",    "Google",                            True),
        ("Azure AZ-900",           "CLOUD",    "Microsoft",                         True),
        ("Azure AZ-104",           "CLOUD",    "Microsoft",                         True),
        ("PMP",                    "PM",       "PMI",                               True),
        ("情報処理技術者（基本情報）",     "OTHER",    "IPA",                               False),
        ("情報処理技術者（応用情報）",     "OTHER",    "IPA",                               False),
        ("CKA（Kubernetes管理者）",  "NETWORK",  "CNCF",                              True),
    ]

    op.bulk_insert(
        sa.table(
            "certification_masters",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("category", sa.String),
            sa.column("issuer", sa.String),
            sa.column("has_expiry", sa.Boolean),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {
                "id": str(uuid.uuid4()),
                "name": name,
                "category": category,
                "issuer": issuer,
                "has_expiry": has_expiry,
                "is_active": True,
            }
            for name, category, issuer, has_expiry in cert_masters_seed
        ],
    )


def downgrade() -> None:
    op.drop_table("approval_history")
    op.drop_table("employee_certifications")
    op.drop_table("certification_masters")
    op.drop_table("employee_skills")
    op.drop_table("skills")
    op.drop_table("skill_categories")
    for enum_name in ["approval_status", "cert_category", "approval_action"]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
