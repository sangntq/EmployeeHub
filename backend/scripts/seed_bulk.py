"""
大量テストデータ投入スクリプト（Bulk Seed）

実行方法:
  docker compose exec backend python scripts/seed_bulk.py

投入データ:
  - 部署:       5 件
  - プロジェクト: 10 件
  - 社員:      1000 名（既存 admin を含め 1001+ 名）
  - スキル:    各社員 3-6 件（60% シニア Lv4-5 / 40% ジュニア Lv1-3）
  - 稼働状況:  1000 件
  - アサイン:  ASSIGNED 社員のみ（約 400 件）
  - ビザ情報:  HANOI/HCMC 社員のみ（約 400 件）
"""
import sys
import uuid
import asyncio
import random
from decimal import Decimal
from datetime import date, datetime, timedelta, UTC

sys.path.insert(0, "/app")

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User
from app.models.employee import Employee
from app.models.department import Department
from app.models.skill import Skill, EmployeeSkill
from app.models.work_status import WorkStatus, Assignment
from app.models.project import Project, VisaInfo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── 名前プール ───────────────────────────────────────────────────────────────
SURNAMES_JA = [
    "田中", "鈴木", "佐藤", "山田", "中村",
    "小林", "加藤", "吉田", "山本", "伊藤",
    "渡辺", "松本", "斎藤", "中島", "山口",
    "小川", "木村", "橋本", "石川", "林",
]
FIRSTNAMES_JA = [
    "翔太", "健太", "大輝", "悠斗", "朝陽",
    "拓也", "遼",   "航平", "健二", "太郎",
    "美咲", "陽菜", "花子", "奈々", "千夏",
    "麻衣", "里沙", "由美", "愛子", "明日香",
]

# ── ロール配布 ───────────────────────────────────────────────────────────────
# index 0..19    = manager       (20名, 2%)
# index 20..29   = department_head (10名, 1%)
# index 30..44   = sales         (15名, 1.5%)
# index 45..49   = director      (5名, 0.5%)
# index 50..999  = member        (950名, 95%)
def _get_role(i: int) -> str:
    if i < 20:   return "manager"
    if i < 30:   return "department_head"
    if i < 45:   return "sales"
    if i < 50:   return "director"
    return "member"


# ── 稼働状況の重み ─────────────────────────────────────────────────────────
WORK_STATUS_WEIGHTS = [
    "ASSIGNED",       "ASSIGNED",       "ASSIGNED",       "ASSIGNED",   # 40%
    "FREE_IMMEDIATE", "FREE_IMMEDIATE", "FREE_IMMEDIATE",               # 30%
    "FREE_PLANNED",   "FREE_PLANNED",                                   # 20%
    "INTERNAL",                                                         # 10%
]

# ── プロジェクトマスタ定義 ───────────────────────────────────────────────────
PROJECT_TEMPLATES = [
    ("ECサイトリニューアル",     "株式会社サンプル商事",   "EC・小売"),
    ("基幹システム刷新",         "ABC製造株式会社",       "製造業"),
    ("モバイルアプリ開発",       "XYZフィンテック",       "金融"),
    ("クラウド移行PJ",          "大手流通グループ",       "流通"),
    ("DXコンサルティング",      "TUV保険",               "保険"),
    ("社内ポータル構築",         "EFG商社",               "商社"),
    ("AIチャットボット開発",     "HIJ通信",               "通信"),
    ("ERPカスタマイズ",         "KLM化学",               "化学"),
    ("セキュリティ診断",         "NOP銀行",               "銀行・金融"),
    ("データ分析基盤構築",       "QRS製薬",               "製薬"),
]

VISA_TYPES = [
    "技術・人文知識・国際業務",
    "高度専門職",
    "企業内転勤",
]

TOTAL = 1000


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as db:
        print("🌱 Bulk Seed 開始...\n")

        # ── Step 1: 部署マスタ ────────────────────────────────────────────
        print("🏢 [Step 1] 部署マスタ作成...")
        dept_defs = [
            ("開発部",                   "Development",        None),
            ("インフラ部",               "Infrastructure",     None),
            ("PM・コンサルティング部",   "PM & Consulting",    None),
            ("QA・テスト部",             "QA & Testing",       None),
            ("営業・ソリューション部",   "Sales & Solutions",  None),
        ]
        dept_ids: list[str] = []
        for idx, (name_ja, name_en, name_vi) in enumerate(dept_defs):
            ex = await db.execute(select(Department).where(Department.name_ja == name_ja))
            dept = ex.scalar_one_or_none()
            if dept is None:
                dept = Department(
                    id=str(uuid.uuid4()),
                    name_ja=name_ja,
                    name_en=name_en,
                    name_vi=name_vi,
                    sort_order=idx + 1,
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
                db.add(dept)
                await db.flush()
                print(f"  ✚ {name_ja}")
            dept_ids.append(dept.id)
        print(f"  → {len(dept_ids)} 件完了\n")

        # ── Step 2: スキルID一覧を取得 ────────────────────────────────────
        print("🛠  [Step 2] スキルマスタ取得...")
        skill_res = await db.execute(select(Skill.id).where(Skill.is_active == True))
        skill_ids: list[str] = [row[0] for row in skill_res.all()]
        if not skill_ids:
            print("❌ スキルマスタが空です。先に `alembic upgrade head` を実行してください。")
            return
        print(f"  → {len(skill_ids)} 件取得\n")

        # ── Step 3: admin 社員 ID を取得 ─────────────────────────────────
        print("🔑 [Step 3] admin ID 取得...")
        admin_res = await db.execute(
            select(Employee.id).where(Employee.system_role == "admin").limit(1)
        )
        admin_id: str | None = admin_res.scalar_one_or_none()
        if not admin_id:
            print("❌ admin 社員が見つかりません。先に `alembic upgrade head` を実行してください。")
            return
        print(f"  → {admin_id[:8]}...\n")

        # ── Step 4: 社員 1000 名を作成 ───────────────────────────────────
        print(f"👥 [Step 4] 社員 {TOTAL} 名を生成...")

        # (Employee オブジェクト, index, work_status) のリスト
        emp_list: list[tuple[Employee, int, str]] = []
        new_count = 0
        skip_count = 0

        for i in range(TOTAL):
            emp_num = f"EMP-{i + 1:04d}"
            ws_status = WORK_STATUS_WEIGHTS[i % len(WORK_STATUS_WEIGHTS)]

            # 冪等チェック
            ex = await db.execute(
                select(Employee).where(Employee.employee_number == emp_num)
            )
            emp = ex.scalar_one_or_none()
            if emp is not None:
                emp_list.append((emp, i, ws_status))
                skip_count += 1
                continue

            role = _get_role(i)
            name_ja = f"{SURNAMES_JA[i % 20]}{FIRSTNAMES_JA[(i // 20) % 20]}"

            # 管理系ロールのみユーザーアカウントを作成（ログイン可能にする）
            user_id: str | None = None
            if role != "member":
                emp_email = f"emp{i + 1:04d}@employeehub.local"
                # 既存ユーザーチェック（重複防止）
                u_ex = await db.execute(select(User).where(User.email == emp_email))
                user = u_ex.scalar_one_or_none()
                if user is None:
                    user = User(
                        id=str(uuid.uuid4()),
                        email=emp_email,
                        password_hash=pwd_context.hash("Test1234!"),
                        is_active=True,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                    db.add(user)
                    await db.flush()
                user_id = user.id

            # 拠点: HANOI を多め (index 0,1→HANOI, 2→HCMC, 3→TOKYO, 4→OSAKA)
            office = ["HANOI", "HANOI", "HCMC", "TOKYO", "OSAKA"][i % 5]

            emp = Employee(
                id=str(uuid.uuid4()),
                user_id=user_id,
                employee_number=emp_num,
                name_ja=name_ja,
                name_en=f"{SURNAMES_JA[i % 20]} {FIRSTNAMES_JA[(i // 20) % 20]}",
                department_id=dept_ids[i % len(dept_ids)],
                system_role=role,
                office_location=office,
                employment_type=["FULLTIME", "FULLTIME", "FULLTIME", "CONTRACT", "FREELANCE"][i % 5],
                work_style=["REMOTE", "REMOTE", "ONSITE", "HYBRID", "REMOTE"][i % 5],
                joined_at=date(2020 + (i % 5), (i % 12) + 1, 1),
                email=f"emp{i + 1:04d}@employeehub.local",
                japanese_level=["N1", "N2", "N3", "N4", "N5", "NONE"][i % 6],
                is_active=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            db.add(emp)
            emp_list.append((emp, i, ws_status))
            new_count += 1

            # 100 件ごとにフラッシュ
            if new_count % 100 == 0:
                await db.flush()
                print(f"  ... {new_count} 件作成済み")

        await db.flush()
        print(f"  → 新規作成: {new_count} 件 / スキップ（既存）: {skip_count} 件\n")

        # ── Step 5: スキル割り当て ─────────────────────────────────────────
        print("📚 [Step 5] スキル割り当て...")
        skill_total = 0
        processed = 0

        for emp, i, _ in emp_list:
            # 既存スキルがあればスキップ
            ex_sk = await db.execute(
                select(EmployeeSkill.id).where(EmployeeSkill.employee_id == emp.id).limit(1)
            )
            if ex_sk.scalar_one_or_none() is not None:
                processed += 1
                continue

            is_senior = (i % 10) < 6  # 60% シニア

            skill_count = random.randint(4, 6) if is_senior else random.randint(3, 5)
            chosen = random.sample(skill_ids, min(skill_count, len(skill_ids)))

            for skill_id in chosen:
                if is_senior:
                    self_lv = random.choice([3, 4, 4, 5, 5])
                    approved_lv = max(1, self_lv - random.choice([0, 0, 1]))
                    exp_years = Decimal(str(round(random.uniform(3.0, 10.0), 1)))
                    status = "APPROVED"
                else:
                    self_lv = random.choice([1, 2, 2, 3])
                    approved_lv = self_lv
                    exp_years = Decimal(str(round(random.uniform(0.5, 3.0), 1)))
                    # ジュニアは 2/3 が承認済み、1/3 は審査中
                    status = random.choice(["APPROVED", "APPROVED", "PENDING"])

                approved_at = None
                approver_id = None
                if status == "APPROVED":
                    approved_at = datetime.now(UTC) - timedelta(days=random.randint(1, 180))
                    approver_id = admin_id

                db.add(EmployeeSkill(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    skill_id=skill_id,
                    self_level=self_lv,
                    approved_level=approved_lv if status == "APPROVED" else None,
                    experience_years=exp_years,
                    last_used_at=date(2025, random.randint(1, 12), 1) if status == "APPROVED" else None,
                    status=status,
                    approver_id=approver_id,
                    approved_at=approved_at,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                ))
                skill_total += 1

            processed += 1
            if processed % 100 == 0:
                await db.flush()
                print(f"  ... {processed}/{len(emp_list)} 名処理")

        await db.flush()
        print(f"  → スキルレコード: {skill_total} 件\n")

        # ── Step 6: 稼働状況 ───────────────────────────────────────────────
        print("📊 [Step 6] 稼働状況作成...")
        ws_total = 0

        for emp, i, ws_status in emp_list:
            ex_ws = await db.execute(
                select(WorkStatus.id).where(WorkStatus.employee_id == emp.id)
            )
            if ex_ws.scalar_one_or_none() is not None:
                continue

            free_from = None
            if ws_status == "FREE_PLANNED":
                free_from = date(2026, random.randint(4, 12), 1)

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

            if ws_total % 100 == 0:
                await db.flush()

        await db.flush()
        print(f"  → {ws_total} 件\n")

        # ── Step 7: プロジェクトマスタ + アサイン ─────────────────────────
        print("📁 [Step 7] プロジェクト作成...")
        project_objs: list[Project] = []
        for name, client, industry in PROJECT_TEMPLATES:
            ex = await db.execute(select(Project).where(Project.name == name))
            proj = ex.scalar_one_or_none()
            if proj is None:
                proj = Project(
                    id=str(uuid.uuid4()),
                    name=name,
                    client_name=client,
                    industry=industry,
                    started_at=date(2025, 1, 1),
                    ended_at=None,
                    created_by=admin_id,
                    created_at=datetime.now(UTC),
                )
                db.add(proj)
                await db.flush()
                print(f"  ✚ {name}")
            project_objs.append(proj)
        print(f"  → {len(project_objs)} 件完了")

        print("🔗 アサイン作成...")
        asgn_total = 0
        for emp, i, ws_status in emp_list:
            if ws_status != "ASSIGNED":
                continue

            ex_asgn = await db.execute(
                select(Assignment.id).where(Assignment.employee_id == emp.id).limit(1)
            )
            if ex_asgn.scalar_one_or_none() is not None:
                continue

            proj = project_objs[i % len(project_objs)]
            start_month = random.randint(1, 10)
            db.add(Assignment(
                id=str(uuid.uuid4()),
                employee_id=emp.id,
                project_id=proj.id,
                allocation_percent=random.choice([50, 80, 80, 100, 100]),
                started_at=date(2025, start_month, 1),
                ends_at=date(2026, random.randint(3, 12), 28),
                is_active=True,
                created_by=admin_id,
                created_at=datetime.now(UTC),
            ))
            asgn_total += 1

            if asgn_total % 100 == 0:
                await db.flush()

        await db.flush()
        print(f"  → {asgn_total} 件\n")

        # ── Step 8: ビザ情報 ───────────────────────────────────────────────
        print("🛂 [Step 8] ビザ情報作成（HANOI/HCMC 拠点）...")
        visa_total = 0

        for emp, i, _ in emp_list:
            if emp.office_location not in ("HANOI", "HCMC"):
                continue

            ex_visa = await db.execute(
                select(VisaInfo.id).where(VisaInfo.employee_id == emp.id)
            )
            if ex_visa.scalar_one_or_none() is not None:
                continue

            # 20% → 30日以内に期限切れ（Alert Dashboard のアラート対象）
            if i % 5 == 0:
                expires_at = date(2026, 3, random.randint(3, 31))
            else:
                expires_at = date(2027 + (i % 2), random.randint(3, 12), 1)

            db.add(VisaInfo(
                id=str(uuid.uuid4()),
                employee_id=emp.id,
                visa_type=random.choice(VISA_TYPES),
                residence_card_number=f"VN{i + 1:07d}JP",
                expires_at=expires_at,
                notes="在留カード確認済み",
                updated_by=admin_id,
                updated_at=datetime.now(UTC),
            ))
            visa_total += 1

            if visa_total % 100 == 0:
                await db.flush()

        await db.flush()
        print(f"  → {visa_total} 件\n")

        # ── 最終コミット ──────────────────────────────────────────────────
        await db.commit()

        print("=" * 55)
        print("✅  Bulk Seed 完了!")
        print(f"   社員:        {len(emp_list):>5} 名（新規: {new_count}）")
        print(f"   スキル:      {skill_total:>5} 件")
        print(f"   稼働状況:    {ws_total:>5} 件")
        print(f"   アサイン:    {asgn_total:>5} 件")
        print(f"   ビザ情報:    {visa_total:>5} 件")
        print("=" * 55)
        print("\n🌐 確認:")
        print("   http://localhost:3000  →  admin@employeehub.local / Admin1234!")
        print("   管理系ロール           →  emp0001〜emp0050@employeehub.local / Test1234!")


if __name__ == "__main__":
    asyncio.run(seed())
