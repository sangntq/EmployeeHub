"""007: 資格マスタを大幅拡充 — 言語認定・クラウド・PM・DevOps・ローコード等

Revision ID: 007
Revises: 006
Create Date: 2026-03-04
"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None

# 追加する資格マスタ定義
# (name, category, issuer, has_expiry)
NEW_CERT_MASTERS = [
    # ────────────────────────────────────────────────
    # LANGUAGE — 語学・プログラミング言語認定
    # ────────────────────────────────────────────────
    ("TOEIC Listening & Reading (700+)",     "LANGUAGE", "ETS",                             True),
    ("TOEIC Listening & Reading (900+)",     "LANGUAGE", "ETS",                             True),
    ("TOEFL iBT",                            "LANGUAGE", "ETS",                             True),
    ("IELTS Academic",                       "LANGUAGE", "British Council / IDP",           True),
    ("BJT ビジネス日本語能力テスト (J1)",       "LANGUAGE", "一般財団法人日本漢字能力検定協会",     True),
    ("BJT ビジネス日本語能力テスト (J2)",       "LANGUAGE", "一般財団法人日本漢字能力検定協会",     True),
    ("Oracle Certified Java Programmer Silver SE 17", "LANGUAGE", "Oracle",                False),
    ("Oracle Certified Java Programmer Gold SE 17",   "LANGUAGE", "Oracle",                False),
    ("Python Institute PCEP (Entry Programmer)",      "LANGUAGE", "Python Institute",       False),
    ("Python Institute PCAP (Associate Programmer)",  "LANGUAGE", "Python Institute",       False),
    ("Python Institute PCPP1 (Professional Programmer)", "LANGUAGE", "Python Institute",   False),
    ("Zend PHP Certified Engineer",                   "LANGUAGE", "Zend (Perforce)",        True),
    ("Ruby Association Certified Ruby Programmer Silver", "LANGUAGE", "Ruby Association",  False),
    ("Ruby Association Certified Ruby Programmer Gold",   "LANGUAGE", "Ruby Association",  False),
    ("Google Associate Android Developer",            "LANGUAGE", "Google",                True),

    # ────────────────────────────────────────────────
    # CLOUD — クラウドプラットフォーム
    # ────────────────────────────────────────────────
    # AWS 追加
    ("AWS Cloud Practitioner (CLF-C02)",              "CLOUD", "Amazon Web Services",       True),
    ("AWS SysOps Administrator Associate (SOA-C02)",  "CLOUD", "Amazon Web Services",       True),
    ("AWS DevOps Engineer Professional (DOP-C02)",    "CLOUD", "Amazon Web Services",       True),
    ("AWS Advanced Networking Specialty (ANS-C01)",   "CLOUD", "Amazon Web Services",       True),
    ("AWS Security Specialty (SCS-C02)",              "CLOUD", "Amazon Web Services",       True),
    ("AWS Machine Learning Specialty (MLS-C01)",      "CLOUD", "Amazon Web Services",       True),
    ("AWS Data Analytics Specialty (DAS-C01)",        "CLOUD", "Amazon Web Services",       True),
    ("AWS Database Specialty (DBS-C01)",              "CLOUD", "Amazon Web Services",       True),
    # GCP 追加
    ("GCP Cloud Digital Leader",                      "CLOUD", "Google",                    True),
    ("GCP Professional Cloud DevOps Engineer",        "CLOUD", "Google",                    True),
    ("GCP Professional Data Engineer",                "CLOUD", "Google",                    True),
    ("GCP Professional Cloud Developer",              "CLOUD", "Google",                    True),
    ("GCP Professional Cloud Network Engineer",       "CLOUD", "Google",                    True),
    ("GCP Professional Cloud Security Engineer",      "CLOUD", "Google",                    True),
    # Azure 追加
    ("Microsoft Azure Developer Associate (AZ-204)",  "CLOUD", "Microsoft",                 True),
    ("Microsoft Azure Solutions Architect (AZ-305)",  "CLOUD", "Microsoft",                 True),
    ("Microsoft Azure DevOps Engineer (AZ-400)",      "CLOUD", "Microsoft",                 True),
    ("Microsoft Azure Data Fundamentals (DP-900)",    "CLOUD", "Microsoft",                 True),
    ("Microsoft Azure Data Scientist (DP-100)",       "CLOUD", "Microsoft",                 True),
    ("Microsoft Azure AI Fundamentals (AI-900)",      "CLOUD", "Microsoft",                 True),
    # Oracle Cloud Infrastructure
    ("OCI Foundations 2023 Associate (1Z0-1085)",     "CLOUD", "Oracle",                    True),
    ("OCI Architect Associate (1Z0-1072)",            "CLOUD", "Oracle",                    True),
    ("OCI Architect Professional (1Z0-997)",          "CLOUD", "Oracle",                    True),
    # Alibaba Cloud（ベトナム市場で重要）
    ("Alibaba Cloud ACA (Associate Cloud Engineer)",  "CLOUD", "Alibaba Cloud",             True),
    ("Alibaba Cloud ACP (Professional)",              "CLOUD", "Alibaba Cloud",             True),
    ("Alibaba Cloud ACE (Expert)",                    "CLOUD", "Alibaba Cloud",             True),
    # Salesforce
    ("Salesforce Certified Administrator",            "CLOUD", "Salesforce",                True),
    ("Salesforce Platform Developer I",               "CLOUD", "Salesforce",                True),
    ("Salesforce Platform Developer II",              "CLOUD", "Salesforce",                True),
    ("Salesforce Application Architect",              "CLOUD", "Salesforce",                True),
    ("Salesforce Marketing Cloud Administrator",      "CLOUD", "Salesforce",                True),
    # ServiceNow
    ("ServiceNow Certified System Administrator (CSA)",        "CLOUD", "ServiceNow",       True),
    ("ServiceNow Certified Implementation Specialist (CIS-ITSM)", "CLOUD", "ServiceNow",   True),
    ("ServiceNow Certified Application Developer (CAD)",       "CLOUD", "ServiceNow",       True),
    # Microsoft 365
    ("Microsoft 365 Fundamentals (MS-900)",           "CLOUD", "Microsoft",                 True),
    ("Microsoft 365 Administrator Expert (MS-102)",   "CLOUD", "Microsoft",                 True),
    ("Microsoft Power Platform Fundamentals (PL-900)","CLOUD", "Microsoft",                 True),

    # ────────────────────────────────────────────────
    # PM — プロジェクト管理
    # ────────────────────────────────────────────────
    ("CAPM (Certified Associate in PM)",              "PM", "PMI",                          True),
    ("PMI-ACP (Agile Certified Practitioner)",        "PM", "PMI",                          True),
    ("PRINCE2 Foundation",                            "PM", "PeopleCert / Axelos",          True),
    ("PRINCE2 Practitioner",                          "PM", "PeopleCert / Axelos",          True),
    ("Professional Scrum Master I (PSM I)",           "PM", "Scrum.org",                    False),
    ("Professional Scrum Master II (PSM II)",         "PM", "Scrum.org",                    False),
    ("Professional Scrum Product Owner (PSPO I)",     "PM", "Scrum.org",                    False),
    ("Certified ScrumMaster (CSM)",                   "PM", "Scrum Alliance",               True),
    ("SAFe 5 Agilist",                                "PM", "Scaled Agile",                 True),
    ("ITIL 4 Foundation",                             "PM", "PeopleCert / Axelos",          True),
    ("ITIL 4 Specialist",                             "PM", "PeopleCert / Axelos",          True),

    # ────────────────────────────────────────────────
    # NETWORK — ネットワーク・インフラ
    # ────────────────────────────────────────────────
    ("CompTIA Network+",                              "NETWORK", "CompTIA",                 True),
    ("CompTIA Linux+",                                "NETWORK", "CompTIA",                 True),
    ("Cisco CCNA",                                    "NETWORK", "Cisco",                   True),
    ("Cisco CCNP Enterprise",                         "NETWORK", "Cisco",                   True),
    ("Cisco CCIE Enterprise Infrastructure",          "NETWORK", "Cisco",                   True),
    ("LPIC-1 (Linux Administrator)",                  "NETWORK", "Linux Professional Institute", True),
    ("LPIC-2 (Linux Engineer)",                       "NETWORK", "Linux Professional Institute", True),
    ("LPIC-3 Mixed Environment",                      "NETWORK", "Linux Professional Institute", True),
    ("Red Hat RHCSA",                                 "NETWORK", "Red Hat",                 True),
    ("Red Hat RHCE",                                  "NETWORK", "Red Hat",                 True),

    # ────────────────────────────────────────────────
    # SECURITY — セキュリティ
    # ────────────────────────────────────────────────
    ("CompTIA Security+",                             "SECURITY", "CompTIA",                True),
    ("CompTIA CySA+ (Cybersecurity Analyst)",         "SECURITY", "CompTIA",                True),
    ("CompTIA PenTest+",                              "SECURITY", "CompTIA",                True),
    ("CISSP",                                         "SECURITY", "ISC2",                   True),
    ("CISM (Certified Information Security Manager)", "SECURITY", "ISACA",                  True),
    ("CEH (Certified Ethical Hacker)",                "SECURITY", "EC-Council",             True),
    ("CISA (Certified Information Systems Auditor)",  "SECURITY", "ISACA",                  True),
    ("情報処理安全確保支援士 (SC)",                     "SECURITY", "IPA",                    False),

    # ────────────────────────────────────────────────
    # OTHER — DevOps / コンテナ
    # ────────────────────────────────────────────────
    ("CKAD (Certified Kubernetes Application Developer)", "OTHER", "CNCF",                  True),
    ("CKS (Certified Kubernetes Security Specialist)",    "OTHER", "CNCF",                  True),
    ("Docker Certified Associate (DCA)",                  "OTHER", "Mirantis",              True),
    ("HashiCorp Certified Terraform Associate",           "OTHER", "HashiCorp",             True),
    ("HashiCorp Vault Associate",                         "OTHER", "HashiCorp",             True),
    ("GitHub Foundations",                                "OTHER", "GitHub",                True),
    ("GitLab Certified Associate",                        "OTHER", "GitLab",                True),

    # OTHER — データベース
    ("Oracle Database SQL Certified Associate",           "OTHER", "Oracle",                False),
    ("Oracle Database Administrator Certified Professional", "OTHER", "Oracle",             False),
    ("MySQL Database Administrator (Oracle)",             "OTHER", "Oracle",                False),
    ("MongoDB Associate Developer (C100DEV)",             "OTHER", "MongoDB",               True),
    ("MongoDB Associate Database Administrator (C100DBA)","OTHER", "MongoDB",               True),
    ("Databricks Certified Associate Developer",          "OTHER", "Databricks",            True),
    ("Snowflake SnowPro Core",                            "OTHER", "Snowflake",             True),

    # OTHER — IPA 高度区分（追加）
    ("ネットワークスペシャリスト (NW)",                   "OTHER", "IPA",                    False),
    ("データベーススペシャリスト (DB)",                   "OTHER", "IPA",                    False),
    ("プロジェクトマネージャ試験 (PM)",                   "OTHER", "IPA",                    False),
    ("システムアーキテクト (SA)",                         "OTHER", "IPA",                    False),
    ("ITストラテジスト (ST)",                             "OTHER", "IPA",                    False),
    ("システム監査技術者 (AU)",                           "OTHER", "IPA",                    False),
    ("エンベデッドシステムスペシャリスト (ES)",            "OTHER", "IPA",                    False),
    ("ITパスポート試験 (IP)",                             "OTHER", "IPA",                    False),

    # OTHER — ローコード / ノーコード
    ("Microsoft Power Apps Developer (PL-400)",           "OTHER", "Microsoft",             True),
    ("Microsoft Power Automate (PL-200)",                 "OTHER", "Microsoft",             True),
    ("Microsoft Power BI Data Analyst (PL-300)",          "OTHER", "Microsoft",             True),
    ("OutSystems Professional Developer",                 "OTHER", "OutSystems",            True),
    ("OutSystems Associate Reactive Developer",           "OTHER", "OutSystems",            True),
    ("Mendix Rapid Developer",                            "OTHER", "Mendix",                True),
    ("Mendix Advanced Developer",                         "OTHER", "Mendix",                True),
    ("Appian Associate Developer",                        "OTHER", "Appian",                True),
    ("Appian Senior Developer",                           "OTHER", "Appian",                True),
    ("Pega Certified System Architect (CSA)",             "OTHER", "Pegasystems",           True),
    ("Pega Certified Senior System Architect (CSSA)",     "OTHER", "Pegasystems",           True),

    # OTHER — SaaS ツール認定
    ("Google Workspace Administrator",                    "OTHER", "Google",                True),
    ("HubSpot Marketing Software Certification",          "OTHER", "HubSpot",               True),
    ("HubSpot Sales Software Certification",              "OTHER", "HubSpot",               True),
    ("Atlassian Certified in Jira Administration (Server)", "OTHER", "Atlassian",           True),
    ("Zendesk Support Administrator Certification",       "OTHER", "Zendesk",               True),
    ("Tableau Desktop Specialist",                        "OTHER", "Tableau / Salesforce",  True),
    ("Tableau Certified Data Analyst",                    "OTHER", "Tableau / Salesforce",  True),
    ("AWS QuickSight Business Intelligence Specialty",    "OTHER", "Amazon Web Services",    True),
]


def upgrade() -> None:
    op.bulk_insert(
        sa.table(
            "certification_masters",
            sa.column("id",         sa.String),
            sa.column("name",       sa.String),
            sa.column("category",   sa.String),
            sa.column("issuer",     sa.String),
            sa.column("has_expiry", sa.Boolean),
            sa.column("is_active",  sa.Boolean),
        ),
        [
            {
                "id":         str(uuid.uuid4()),
                "name":       name,
                "category":   category,
                "issuer":     issuer,
                "has_expiry": has_expiry,
                "is_active":  True,
            }
            for name, category, issuer, has_expiry in NEW_CERT_MASTERS
        ],
    )


def downgrade() -> None:
    # 本マイグレーションで追加した名前のレコードのみ削除
    names = [name for name, _, _, _ in NEW_CERT_MASTERS]
    placeholders = ", ".join(f"'{n.replace(chr(39), chr(39)+chr(39))}'" for n in names)
    op.execute(f"DELETE FROM certification_masters WHERE name IN ({placeholders})")
