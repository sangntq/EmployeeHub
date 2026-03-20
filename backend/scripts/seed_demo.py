"""
デモ用少数データ投入スクリプト（10名）

実行方法:
  docker compose exec backend python scripts/seed_demo.py

投入データ:
  - 部署:       5 件
  - プロジェクト: 5 件
  - 社員:       10 名（全員ログイン可能）
  - スキル:     各社員 3-5 件（APPROVED）
  - 資格:       各社員 1-3 件
  - 稼働状況:   10 件
  - アサイン:   ASSIGNED 社員のみ
  - ビザ情報:   ベトナム拠点社員のみ
  - PJ経歴:     各社員 1-2 件

テストアカウント:
  admin@employeehub.local / Admin1234!  (既存admin)
  demo01〜demo10@employeehub.local / Demo1234!
"""
import sys
import uuid
import asyncio
from decimal import Decimal
from datetime import date, datetime, timedelta, UTC

sys.path.insert(0, "/app")

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User
from app.models.employee import Employee
from app.models.department import Department
from app.models.skill import Skill, SkillCategory, EmployeeSkill
from app.models.certification import CertificationMaster, EmployeeCertification
from app.models.work_status import WorkStatus, Assignment
from app.models.project import Project, VisaInfo, EmployeeProject

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PASSWORD = "Demo1234!"

# ── 10名の社員プロフィール定義 ───────────────────────────────────────────────
EMPLOYEES = [
    {
        "number": "DEMO-0001",
        "email": "demo01@employeehub.local",
        "name_ja": "グエン・ヴァン・ミン",
        "name_en": "Nguyen Van Minh",
        "name_vi": "Nguyễn Văn Minh",
        "role": "manager",
        "office": "HANOI",
        "type": "FULLTIME",
        "style": "REMOTE",
        "joined": date(2019, 4, 1),
        "japanese_level": "N2",
        "self_pr": "10年以上のWeb開発経験。Java/Pythonバックエンド、React/Vueフロントエンドの両方に精通。チームリードとして15名規模のプロジェクトを成功に導いた実績あり。",
        "work_status": "ASSIGNED",
    },
    {
        "number": "DEMO-0002",
        "email": "demo02@employeehub.local",
        "name_ja": "チャン・ティ・ラン",
        "name_en": "Tran Thi Lan",
        "name_vi": "Trần Thị Lan",
        "role": "department_head",
        "office": "HANOI",
        "type": "FULLTIME",
        "style": "HYBRID",
        "joined": date(2018, 1, 15),
        "japanese_level": "N1",
        "self_pr": "PM・コンサルティング部門の責任者。PMP取得済み。日本顧客との折衝経験が豊富で、大規模SIプロジェクトの管理に強み。",
        "work_status": "ASSIGNED",
    },
    {
        "number": "DEMO-0003",
        "email": "demo03@employeehub.local",
        "name_ja": "レ・ホアン・ナム",
        "name_en": "Le Hoang Nam",
        "name_vi": "Lê Hoàng Nam",
        "role": "member",
        "office": "HCMC",
        "type": "FULLTIME",
        "style": "ONSITE",
        "joined": date(2022, 7, 1),
        "japanese_level": "N3",
        "self_pr": "クラウドインフラ構築が得意。AWS SAA取得済み。Terraform/Kubernetesを使ったIaC運用の経験あり。",
        "work_status": "FREE_IMMEDIATE",
    },
    {
        "number": "DEMO-0004",
        "email": "demo04@employeehub.local",
        "name_ja": "ファム・ドゥック・アン",
        "name_en": "Pham Duc Anh",
        "name_vi": "Phạm Đức Anh",
        "role": "member",
        "office": "HANOI",
        "type": "FULLTIME",
        "style": "REMOTE",
        "joined": date(2021, 3, 1),
        "japanese_level": "N2",
        "self_pr": "Reactフロントエンド開発を中心に3年以上の経験。TypeScript、Next.js、TailwindCSSに精通。UI/UX改善の提案力が強み。",
        "work_status": "ASSIGNED",
    },
    {
        "number": "DEMO-0005",
        "email": "demo05@employeehub.local",
        "name_ja": "ヴォー・ティ・フォン",
        "name_en": "Vo Thi Phuong",
        "name_vi": "Võ Thị Phương",
        "role": "member",
        "office": "HCMC",
        "type": "FULLTIME",
        "style": "HYBRID",
        "joined": date(2023, 1, 10),
        "japanese_level": "N4",
        "self_pr": "QAエンジニアとしてテスト自動化を推進。Selenium/Playwrightの経験あり。品質向上とテスト効率化に貢献。",
        "work_status": "FREE_PLANNED",
    },
    {
        "number": "DEMO-0006",
        "email": "demo06@employeehub.local",
        "name_ja": "田中 太郎",
        "name_en": "Tanaka Taro",
        "role": "sales",
        "office": "TOKYO",
        "type": "FULLTIME",
        "style": "HYBRID",
        "joined": date(2020, 4, 1),
        "japanese_level": None,
        "self_pr": "IT人材提案営業として5年の経験。日本の金融・製造業界に幅広いネットワークを保有。",
        "work_status": "INTERNAL",
    },
    {
        "number": "DEMO-0007",
        "email": "demo07@employeehub.local",
        "name_ja": "ブイ・クアン・フイ",
        "name_en": "Bui Quang Huy",
        "name_vi": "Bùi Quang Huy",
        "role": "member",
        "office": "HANOI",
        "type": "CONTRACT",
        "style": "REMOTE",
        "joined": date(2024, 6, 1),
        "japanese_level": "N3",
        "self_pr": "Pythonバックエンド開発者。FastAPI/Djangoの経験豊富。機械学習モデルのAPI化も対応可能。",
        "work_status": "ASSIGNED",
    },
    {
        "number": "DEMO-0008",
        "email": "demo08@employeehub.local",
        "name_ja": "鈴木 美咲",
        "name_en": "Suzuki Misaki",
        "role": "director",
        "office": "TOKYO",
        "type": "FULLTIME",
        "style": "ONSITE",
        "joined": date(2017, 4, 1),
        "japanese_level": None,
        "self_pr": "事業戦略立案と組織マネジメントに15年の経験。オフショア開発事業の立ち上げ実績あり。",
        "work_status": "INTERNAL",
    },
    {
        "number": "DEMO-0009",
        "email": "demo09@employeehub.local",
        "name_ja": "ダン・ミン・トゥアン",
        "name_en": "Dang Minh Thuan",
        "name_vi": "Đặng Minh Thuận",
        "role": "member",
        "office": "HCMC",
        "type": "FULLTIME",
        "style": "REMOTE",
        "joined": date(2020, 10, 1),
        "japanese_level": "N2",
        "self_pr": "フルスタックエンジニア。Java/Spring Boot + React/TypeScriptの組み合わせが最も得意。CI/CDパイプライン構築の経験もあり。",
        "work_status": "ASSIGNED",
    },
    {
        "number": "DEMO-0010",
        "email": "demo10@employeehub.local",
        "name_ja": "ホアン・ティ・トゥイ",
        "name_en": "Hoang Thi Thuy",
        "name_vi": "Hoàng Thị Thủy",
        "role": "member",
        "office": "HANOI",
        "type": "FREELANCE",
        "style": "REMOTE",
        "joined": date(2025, 1, 15),
        "japanese_level": "N5",
        "self_pr": "モバイルアプリ開発（Flutter/React Native）が専門。iOS/Androidの両プラットフォーム開発経験あり。",
        "work_status": "FREE_IMMEDIATE",
    },
]

# ── スキル割り当て定義（社員番号 → スキル名リスト）─────────────────────────
# スキルマスタの name フィールドで照合する
EMPLOYEE_SKILLS = {
    "DEMO-0001": [
        ("Java", 5, 5, Decimal("10.0")),
        ("Python", 4, 4, Decimal("5.0")),
        ("React", 4, 4, Decimal("4.0")),
        ("PostgreSQL", 4, 3, Decimal("8.0")),
        ("Docker", 3, 3, Decimal("3.0")),
    ],
    "DEMO-0002": [
        ("Excel VBA", 3, 3, Decimal("5.0")),
        ("SQL Server", 3, 3, Decimal("6.0")),
        ("Python", 2, 2, Decimal("2.0")),
    ],
    "DEMO-0003": [
        ("AWS", 4, 4, Decimal("3.0")),
        ("Docker", 4, 4, Decimal("3.0")),
        ("Kubernetes", 3, 3, Decimal("2.0")),
        ("Terraform", 3, 3, Decimal("2.0")),
        ("Linux", 4, 4, Decimal("4.0")),
    ],
    "DEMO-0004": [
        ("React", 5, 4, Decimal("3.5")),
        ("TypeScript", 4, 4, Decimal("3.5")),
        ("JavaScript", 5, 5, Decimal("5.0")),
        ("HTML/CSS", 4, 4, Decimal("5.0")),
    ],
    "DEMO-0005": [
        ("Selenium", 3, 3, Decimal("2.0")),
        ("Python", 3, 3, Decimal("2.0")),
        ("JavaScript", 2, 2, Decimal("1.5")),
    ],
    "DEMO-0006": [
        ("Excel VBA", 2, 2, Decimal("3.0")),
    ],
    "DEMO-0007": [
        ("Python", 4, 4, Decimal("4.0")),
        ("FastAPI", 4, 3, Decimal("2.0")),
        ("Django", 3, 3, Decimal("3.0")),
        ("PostgreSQL", 3, 3, Decimal("3.0")),
    ],
    "DEMO-0008": [],
    "DEMO-0009": [
        ("Java", 4, 4, Decimal("5.0")),
        ("Spring Boot", 4, 4, Decimal("4.0")),
        ("React", 3, 3, Decimal("3.0")),
        ("TypeScript", 3, 3, Decimal("2.5")),
        ("Docker", 3, 3, Decimal("2.0")),
    ],
    "DEMO-0010": [
        ("Flutter", 4, 3, Decimal("2.5")),
        ("React Native", 3, 3, Decimal("2.0")),
        ("Dart", 4, 3, Decimal("2.5")),
        ("JavaScript", 3, 3, Decimal("3.0")),
    ],
}

# ── 資格割り当て定義（社員番号 → 資格名リスト）──────────────────────────────
EMPLOYEE_CERTS = {
    "DEMO-0001": [
        ("JLPT N2", date(2020, 7, 1), None, "APPROVED"),
        ("Oracle Certified Java Programmer Gold SE", date(2019, 3, 15), None, "APPROVED"),
    ],
    "DEMO-0002": [
        ("JLPT N1", date(2018, 12, 1), None, "APPROVED"),
        ("PMP (Project Management Professional)", date(2021, 6, 15), date(2027, 6, 15), "APPROVED"),
    ],
    "DEMO-0003": [
        ("JLPT N3", date(2023, 7, 1), None, "APPROVED"),
        ("AWS Certified Solutions Architect - Associate (SAA)", date(2024, 1, 20), date(2027, 1, 20), "APPROVED"),
    ],
    "DEMO-0004": [
        ("JLPT N2", date(2022, 12, 1), None, "APPROVED"),
    ],
    "DEMO-0005": [
        ("JLPT N4", date(2024, 7, 1), None, "PENDING"),
        ("ISTQB Foundation Level (CTFL)", date(2024, 3, 10), None, "APPROVED"),
    ],
    "DEMO-0006": [],
    "DEMO-0007": [
        ("JLPT N3", date(2024, 12, 1), None, "PENDING"),
    ],
    "DEMO-0008": [],
    "DEMO-0009": [
        ("JLPT N2", date(2021, 7, 1), None, "APPROVED"),
        ("AWS Certified Cloud Practitioner (CLF)", date(2023, 5, 10), date(2026, 5, 10), "APPROVED"),
        ("Oracle Certified Java Programmer Gold SE", date(2022, 9, 1), None, "APPROVED"),
    ],
    "DEMO-0010": [
        ("JLPT N5", date(2025, 7, 1), None, "PENDING"),
    ],
}

# ── プロジェクトマスタ ───────────────────────────────────────────────────────
PROJECT_DEFS = [
    ("ECサイトリニューアル", "株式会社サンプル商事", "EC・小売",
     date(2024, 4, 1), date(2025, 3, 31)),
    ("基幹システム刷新PJ", "ABC製造株式会社", "製造業",
     date(2025, 1, 1), None),
    ("モバイルアプリ開発", "XYZフィンテック", "金融",
     date(2025, 6, 1), None),
    ("クラウド移行PJ", "大手流通グループ", "流通",
     date(2024, 10, 1), date(2025, 9, 30)),
    ("AIチャットボット開発", "HIJ通信", "通信",
     date(2025, 4, 1), None),
]

# ── PJ経歴割り当て ──────────────────────────────────────────────────────────
EMPLOYEE_PROJECTS = {
    "DEMO-0001": [
        {
            "project": "ECサイトリニューアル",
            "role": "PL",
            "started": date(2024, 4, 1),
            "ended": date(2025, 3, 31),
            "tech_stack": ["Java", "Spring Boot", "React", "PostgreSQL", "AWS"],
            "team_size": 10,
            "responsibilities": "プロジェクトリードとしてバックエンドAPI設計・実装を主導。メンバー10名のタスク管理とコードレビューを担当。",
            "achievements": "予定通り納品完了。レスポンスタイムを従来比40%改善。",
            "phases": ["要件定義", "基本設計", "詳細設計", "製造・実装", "結合テスト"],
            "lessons": "大規模ECシステムのマイクロサービス化と段階的移行手法を習得。",
        },
        {
            "project": "基幹システム刷新PJ",
            "role": "PL",
            "started": date(2025, 1, 1),
            "ended": None,
            "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            "team_size": 8,
            "responsibilities": "バックエンドチームリード。API設計、DB設計、CI/CD整備を担当。",
            "achievements": "開発初期フェーズを1週間前倒しで完了。",
            "phases": ["要件定義", "基本設計", "詳細設計", "製造・実装"],
            "lessons": "レガシー基幹システムからのデータ移行設計のノウハウを蓄積。",
        },
    ],
    "DEMO-0002": [
        {
            "project": "基幹システム刷新PJ",
            "role": "PM",
            "started": date(2025, 1, 1),
            "ended": None,
            "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "team_size": 15,
            "responsibilities": "プロジェクト全体の工程管理、顧客折衝、進捗報告を担当。リスク管理とメンバーのアサイン調整を実施。",
            "achievements": "顧客満足度アンケートで最高評価を獲得。",
            "phases": ["要件定義", "基本設計"],
            "lessons": "日本顧客とのオフショア開発における期待値コントロールの重要性を再認識。",
        },
    ],
    "DEMO-0003": [
        {
            "project": "クラウド移行PJ",
            "role": "INFRA",
            "started": date(2024, 10, 1),
            "ended": date(2025, 9, 30),
            "tech_stack": ["AWS", "Terraform", "Docker", "Kubernetes", "Linux"],
            "team_size": 6,
            "responsibilities": "AWSインフラ設計・構築、Terraform でのIaC化、Kubernetes クラスタ運用を担当。",
            "achievements": "インフラコストを月額30%削減。可用性99.9%を達成。",
            "phases": ["基本設計", "詳細設計", "製造・実装", "運用・保守"],
            "lessons": "マルチアカウントAWS環境の設計パターンとコスト最適化手法を習得。",
        },
    ],
    "DEMO-0004": [
        {
            "project": "ECサイトリニューアル",
            "role": "SE",
            "started": date(2024, 4, 1),
            "ended": date(2025, 3, 31),
            "tech_stack": ["React", "TypeScript", "Next.js", "TailwindCSS"],
            "team_size": 10,
            "responsibilities": "フロントエンド開発全般。商品一覧・検索・カート機能のUI実装。レスポンシブ対応。",
            "achievements": "Lighthouse スコアを60→92に改善。ページ読込時間を50%短縮。",
            "phases": ["詳細設計", "製造・実装", "単体テスト", "結合テスト"],
            "lessons": "大規模SPAのパフォーマンス最適化とコード分割の実践知識を習得。",
        },
        {
            "project": "AIチャットボット開発",
            "role": "SE",
            "started": date(2025, 4, 1),
            "ended": None,
            "tech_stack": ["React", "TypeScript", "Python", "FastAPI"],
            "team_size": 5,
            "responsibilities": "チャットUI開発、WebSocket通信の実装を担当。",
            "achievements": None,
            "phases": ["詳細設計", "製造・実装"],
            "lessons": None,
        },
    ],
    "DEMO-0005": [
        {
            "project": "ECサイトリニューアル",
            "role": "QA",
            "started": date(2024, 6, 1),
            "ended": date(2025, 3, 31),
            "tech_stack": ["Selenium", "Python", "Playwright", "JIRA"],
            "team_size": 10,
            "responsibilities": "テスト計画策定、テストケース作成、自動化テスト(E2E)の実装・運用を担当。",
            "achievements": "E2Eテスト自動化率を70%に向上。リグレッションバグを50%削減。",
            "phases": ["単体テスト", "結合テスト", "総合テスト"],
            "lessons": "テスト自動化の導入戦略と運用保守コストのバランスを学習。",
        },
    ],
    "DEMO-0007": [
        {
            "project": "AIチャットボット開発",
            "role": "SE",
            "started": date(2025, 4, 1),
            "ended": None,
            "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis", "Claude API"],
            "team_size": 5,
            "responsibilities": "バックエンドAPI開発。Claude APIとの連携、対話履歴管理、RAG機能の実装を担当。",
            "achievements": None,
            "phases": ["詳細設計", "製造・実装"],
            "lessons": None,
        },
    ],
    "DEMO-0009": [
        {
            "project": "基幹システム刷新PJ",
            "role": "SE",
            "started": date(2025, 1, 1),
            "ended": None,
            "tech_stack": ["Java", "Spring Boot", "React", "TypeScript", "PostgreSQL", "Docker"],
            "team_size": 15,
            "responsibilities": "フルスタック担当。バックエンドAPIとフロントエンド画面の両方を開発。DB設計にも参加。",
            "achievements": "担当モジュールのユニットテストカバレッジ90%を達成。",
            "phases": ["詳細設計", "製造・実装", "単体テスト"],
            "lessons": "大規模チーム開発でのGitブランチ戦略とCI/CD運用を経験。",
        },
        {
            "project": "クラウド移行PJ",
            "role": "SE",
            "started": date(2024, 10, 1),
            "ended": date(2025, 9, 30),
            "tech_stack": ["Java", "Spring Boot", "Docker", "AWS"],
            "team_size": 6,
            "responsibilities": "既存Javaアプリのコンテナ化、Docker化対応を担当。",
            "achievements": "デプロイ時間を1時間→10分に短縮。",
            "phases": ["詳細設計", "製造・実装", "結合テスト", "運用・保守"],
            "lessons": "Javaアプリのコンテナ化における注意点（JVMメモリ設定等）を習得。",
        },
    ],
    "DEMO-0010": [
        {
            "project": "モバイルアプリ開発",
            "role": "SE",
            "started": date(2025, 6, 1),
            "ended": None,
            "tech_stack": ["Flutter", "Dart", "Firebase", "REST API"],
            "team_size": 4,
            "responsibilities": "Flutter でのモバイルアプリ開発。iOS/Android共通UIの実装を担当。",
            "achievements": None,
            "phases": ["詳細設計", "製造・実装"],
            "lessons": None,
        },
    ],
}


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as db:
        print("🌱 デモデータ投入開始（10名）...\n")

        # ── Step 1: 部署マスタ ────────────────────────────────────────────
        print("🏢 [Step 1] 部署マスタ確認/作成...")
        dept_defs = [
            ("開発部", "Development"),
            ("インフラ部", "Infrastructure"),
            ("PM・コンサルティング部", "PM & Consulting"),
            ("QA・テスト部", "QA & Testing"),
            ("営業・ソリューション部", "Sales & Solutions"),
        ]
        dept_map: dict[str, str] = {}  # name_ja → id
        for idx, (name_ja, name_en) in enumerate(dept_defs):
            ex = await db.execute(select(Department).where(Department.name_ja == name_ja))
            dept = ex.scalar_one_or_none()
            if dept is None:
                dept = Department(
                    id=str(uuid.uuid4()),
                    name_ja=name_ja,
                    name_en=name_en,
                    sort_order=idx + 1,
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
                db.add(dept)
                await db.flush()
                print(f"  ✚ {name_ja}")
            dept_map[name_ja] = dept.id

        # 社員→部署マッピング
        emp_dept = {
            "DEMO-0001": "開発部",
            "DEMO-0002": "PM・コンサルティング部",
            "DEMO-0003": "インフラ部",
            "DEMO-0004": "開発部",
            "DEMO-0005": "QA・テスト部",
            "DEMO-0006": "営業・ソリューション部",
            "DEMO-0007": "開発部",
            "DEMO-0008": "PM・コンサルティング部",
            "DEMO-0009": "開発部",
            "DEMO-0010": "開発部",
        }

        # ── Step 2: スキルマスタ取得 ──────────────────────────────────────
        print("\n🛠  [Step 2] スキルマスタ取得...")
        skill_res = await db.execute(select(Skill).where(Skill.is_active == True))
        all_skills = skill_res.scalars().all()
        skill_name_map: dict[str, str] = {s.name: s.id for s in all_skills}
        print(f"  → {len(skill_name_map)} 件取得")

        # ── Step 3: 資格マスタ取得 ────────────────────────────────────────
        print("\n🏅 [Step 3] 資格マスタ取得...")
        cert_res = await db.execute(
            select(CertificationMaster).where(CertificationMaster.is_active == True)
        )
        all_certs = cert_res.scalars().all()
        cert_name_map: dict[str, CertificationMaster] = {c.name: c for c in all_certs}
        print(f"  → {len(cert_name_map)} 件取得")

        # ── Step 4: admin ID 取得 ─────────────────────────────────────────
        print("\n🔑 [Step 4] admin ID 取得...")
        admin_res = await db.execute(
            select(Employee.id).where(Employee.system_role == "admin").limit(1)
        )
        admin_id: str | None = admin_res.scalar_one_or_none()
        if not admin_id:
            print("❌ admin 社員が見つかりません。先に alembic upgrade head を実行してください。")
            return
        print(f"  → {admin_id[:8]}...")

        # ── Step 5: 社員10名を作成 ────────────────────────────────────────
        print(f"\n👥 [Step 5] 社員 {len(EMPLOYEES)} 名を生成...")
        emp_objs: dict[str, Employee] = {}  # number → Employee

        for emp_def in EMPLOYEES:
            emp_num = emp_def["number"]

            # 冪等チェック
            ex = await db.execute(
                select(Employee).where(Employee.employee_number == emp_num)
            )
            emp = ex.scalar_one_or_none()
            if emp is not None:
                emp_objs[emp_num] = emp
                print(f"  ⏭ {emp_num} ({emp_def['name_ja']}) — 既存")
                continue

            # User アカウント作成
            email = emp_def["email"]
            u_ex = await db.execute(select(User).where(User.email == email))
            user = u_ex.scalar_one_or_none()
            if user is None:
                user = User(
                    id=str(uuid.uuid4()),
                    email=email,
                    password_hash=pwd_context.hash(PASSWORD),
                    is_active=True,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
                db.add(user)
                await db.flush()

            emp = Employee(
                id=str(uuid.uuid4()),
                user_id=user.id,
                employee_number=emp_num,
                name_ja=emp_def["name_ja"],
                name_en=emp_def.get("name_en"),
                name_vi=emp_def.get("name_vi"),
                department_id=dept_map.get(emp_dept.get(emp_num, "開発部")),
                system_role=emp_def["role"],
                office_location=emp_def["office"],
                employment_type=emp_def["type"],
                work_style=emp_def["style"],
                joined_at=emp_def["joined"],
                email=email,
                japanese_level=emp_def.get("japanese_level"),
                self_pr=emp_def.get("self_pr"),
                is_active=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            db.add(emp)
            emp_objs[emp_num] = emp
            print(f"  ✚ {emp_num} ({emp_def['name_ja']}) [{emp_def['role']}]")

        await db.flush()

        # ── Step 6: スキル割り当て ────────────────────────────────────────
        print(f"\n📚 [Step 6] スキル割り当て...")
        skill_total = 0

        for emp_num, skills in EMPLOYEE_SKILLS.items():
            emp = emp_objs.get(emp_num)
            if emp is None or not skills:
                continue

            # 冪等チェック
            ex_sk = await db.execute(
                select(EmployeeSkill.id).where(EmployeeSkill.employee_id == emp.id).limit(1)
            )
            if ex_sk.scalar_one_or_none() is not None:
                continue

            for skill_name, self_lv, approved_lv, exp_years in skills:
                skill_id = skill_name_map.get(skill_name)
                if skill_id is None:
                    print(f"  ⚠ スキル '{skill_name}' がマスタに見つかりません — スキップ")
                    continue

                db.add(EmployeeSkill(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    skill_id=skill_id,
                    self_level=self_lv,
                    approved_level=approved_lv,
                    experience_years=exp_years,
                    last_used_at=date(2025, 12, 1),
                    status="APPROVED",
                    approver_id=admin_id,
                    approved_at=datetime.now(UTC) - timedelta(days=30),
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                ))
                skill_total += 1

        await db.flush()
        print(f"  → {skill_total} 件")

        # ── Step 7: 資格割り当て ──────────────────────────────────────────
        print(f"\n🏅 [Step 7] 資格割り当て...")
        cert_total = 0

        for emp_num, certs in EMPLOYEE_CERTS.items():
            emp = emp_objs.get(emp_num)
            if emp is None or not certs:
                continue

            # 冪等チェック
            ex_cert = await db.execute(
                select(EmployeeCertification.id)
                .where(EmployeeCertification.employee_id == emp.id)
                .limit(1)
            )
            if ex_cert.scalar_one_or_none() is not None:
                continue

            for cert_name, obtained_at, expires_at, status in certs:
                cert_master = cert_name_map.get(cert_name)
                if cert_master is None:
                    print(f"  ⚠ 資格 '{cert_name}' がマスタに見つかりません — スキップ")
                    continue

                approver_id = admin_id if status in ("APPROVED", "REJECTED") else None
                approved_at = (
                    datetime.now(UTC) - timedelta(days=30)
                    if status in ("APPROVED", "REJECTED")
                    else None
                )

                db.add(EmployeeCertification(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    certification_master_id=cert_master.id,
                    obtained_at=obtained_at,
                    expires_at=expires_at,
                    status=status,
                    approver_id=approver_id,
                    approved_at=approved_at,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                ))
                cert_total += 1

        await db.flush()
        print(f"  → {cert_total} 件")

        # ── Step 8: プロジェクトマスタ ────────────────────────────────────
        print(f"\n📁 [Step 8] プロジェクトマスタ作成...")
        proj_map: dict[str, Project] = {}  # name → Project

        for name, client, industry, started, ended in PROJECT_DEFS:
            ex = await db.execute(select(Project).where(Project.name == name))
            proj = ex.scalar_one_or_none()
            if proj is None:
                proj = Project(
                    id=str(uuid.uuid4()),
                    name=name,
                    client_name=client,
                    industry=industry,
                    started_at=started,
                    ended_at=ended,
                    created_by=admin_id,
                    created_at=datetime.now(UTC),
                )
                db.add(proj)
                await db.flush()
                print(f"  ✚ {name}")
            proj_map[name] = proj

        # ── Step 9: 稼働状況 + アサイン ───────────────────────────────────
        print(f"\n📊 [Step 9] 稼働状況 + アサイン...")
        ws_total = 0
        asgn_total = 0

        # アサイン先PJ
        assign_proj = {
            "DEMO-0001": "基幹システム刷新PJ",
            "DEMO-0002": "基幹システム刷新PJ",
            "DEMO-0004": "AIチャットボット開発",
            "DEMO-0007": "AIチャットボット開発",
            "DEMO-0009": "基幹システム刷新PJ",
        }

        for emp_def in EMPLOYEES:
            emp_num = emp_def["number"]
            emp = emp_objs.get(emp_num)
            if emp is None:
                continue

            ws_status = emp_def["work_status"]

            # 稼働状況
            ex_ws = await db.execute(
                select(WorkStatus.id).where(WorkStatus.employee_id == emp.id)
            )
            if ex_ws.scalar_one_or_none() is None:
                free_from = date(2026, 7, 1) if ws_status == "FREE_PLANNED" else None
                db.add(WorkStatus(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    status=ws_status,
                    free_from=free_from,
                    note=None,
                    updated_by=admin_id,
                    updated_at=datetime.now(UTC),
                ))
                ws_total += 1

            # アサイン（ASSIGNED のみ）
            if ws_status == "ASSIGNED" and emp_num in assign_proj:
                ex_asgn = await db.execute(
                    select(Assignment.id).where(Assignment.employee_id == emp.id).limit(1)
                )
                if ex_asgn.scalar_one_or_none() is None:
                    proj = proj_map.get(assign_proj[emp_num])
                    if proj:
                        db.add(Assignment(
                            id=str(uuid.uuid4()),
                            employee_id=emp.id,
                            project_id=proj.id,
                            allocation_percent=100,
                            started_at=proj.started_at or date(2025, 1, 1),
                            ends_at=date(2026, 6, 30),
                            is_active=True,
                            created_by=admin_id,
                            created_at=datetime.now(UTC),
                        ))
                        asgn_total += 1

        await db.flush()
        print(f"  → 稼働状況: {ws_total} 件 / アサイン: {asgn_total} 件")

        # ── Step 10: ビザ情報 ─────────────────────────────────────────────
        print(f"\n🛂 [Step 10] ビザ情報（ベトナム拠点）...")
        visa_total = 0

        for emp_def in EMPLOYEES:
            emp_num = emp_def["number"]
            emp = emp_objs.get(emp_num)
            if emp is None or emp_def["office"] not in ("HANOI", "HCMC"):
                continue

            ex_visa = await db.execute(
                select(VisaInfo.id).where(VisaInfo.employee_id == emp.id)
            )
            if ex_visa.scalar_one_or_none() is not None:
                continue

            db.add(VisaInfo(
                id=str(uuid.uuid4()),
                employee_id=emp.id,
                visa_type="技術・人文知識・国際業務",
                residence_card_number=f"VN{emp_num[-4:]}JP",
                expires_at=date(2027, 9, 30),
                notes="在留カード確認済み",
                updated_by=admin_id,
                updated_at=datetime.now(UTC),
            ))
            visa_total += 1

        await db.flush()
        print(f"  → {visa_total} 件")

        # ── Step 11: PJ経歴 ──────────────────────────────────────────────
        print(f"\n📋 [Step 11] プロジェクト経歴...")
        ep_total = 0

        for emp_num, projects in EMPLOYEE_PROJECTS.items():
            emp = emp_objs.get(emp_num)
            if emp is None:
                continue

            # 冪等チェック
            ex_ep = await db.execute(
                select(EmployeeProject.id)
                .where(EmployeeProject.employee_id == emp.id)
                .limit(1)
            )
            if ex_ep.scalar_one_or_none() is not None:
                continue

            for sort_idx, proj_def in enumerate(projects):
                proj = proj_map.get(proj_def["project"])
                if proj is None:
                    print(f"  ⚠ PJ '{proj_def['project']}' が見つかりません — スキップ")
                    continue

                db.add(EmployeeProject(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    project_id=proj.id,
                    role=proj_def["role"],
                    started_at=proj_def["started"],
                    ended_at=proj_def.get("ended"),
                    tech_stack=proj_def["tech_stack"],
                    team_size=proj_def["team_size"],
                    responsibilities=proj_def["responsibilities"],
                    achievements=proj_def.get("achievements"),
                    process_phases=proj_def.get("phases"),
                    lessons_learned=proj_def.get("lessons"),
                    sort_order=sort_idx,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                ))
                ep_total += 1

        await db.flush()
        print(f"  → {ep_total} 件")

        # ── コミット ──────────────────────────────────────────────────────
        await db.commit()

        print("\n" + "=" * 55)
        print("✅  デモデータ投入完了!")
        print(f"   社員:        {len(emp_objs):>3} 名")
        print(f"   スキル:      {skill_total:>3} 件")
        print(f"   資格:        {cert_total:>3} 件")
        print(f"   稼働状況:    {ws_total:>3} 件")
        print(f"   アサイン:    {asgn_total:>3} 件")
        print(f"   ビザ情報:    {visa_total:>3} 件")
        print(f"   PJ経歴:      {ep_total:>3} 件")
        print("=" * 55)
        print("\n🌐 ログイン情報:")
        print("   admin: admin@employeehub.local / Admin1234!")
        print("   デモ:  demo01〜demo10@employeehub.local / Demo1234!")
        print("\n📋 ロール一覧:")
        for emp_def in EMPLOYEES:
            print(f"   {emp_def['number']} {emp_def['name_ja']:<20s} [{emp_def['role']:<15s}] {emp_def['office']}")


if __name__ == "__main__":
    asyncio.run(seed())
