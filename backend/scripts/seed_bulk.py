"""
大量テストデータ投入スクリプト（Bulk Seed）

実行方法:
  docker compose exec backend python scripts/seed_bulk.py

投入データ:
  - 部署:       5 件
  - プロジェクト: 10 件
  - 社員:      1000 名（既存 admin を含め 1001+ 名）
  - スキル:    各社員 3-6 件（60% シニア Lv4-5 / 40% ジュニア Lv1-3）
  - 資格:      社員の約 50% に 1-4 件（JLPT / クラウド / PM / ローコード等）
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
from app.models.certification import CertificationMaster, EmployeeCertification
from app.models.work_status import WorkStatus, Assignment
from app.models.project import Project, VisaInfo, EmployeeProject

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

        # ── Step 3: 資格マスタを取得・分類 ───────────────────────────────
        print("🏅 [Step 3] 資格マスタ取得・分類...")
        cert_res = await db.execute(
            select(CertificationMaster).where(CertificationMaster.is_active == True)
        )
        all_certs = cert_res.scalars().all()
        if not all_certs:
            print("❌ 資格マスタが空です。先に `alembic upgrade head` を実行してください。")
            return

        # カテゴリ別分類
        cert_by_cat: dict[str, list[CertificationMaster]] = {}
        for c in all_certs:
            cat = str(c.category)
            cert_by_cat.setdefault(cat, []).append(c)

        # JLPT レベルマップ（N1〜N5 → 対応 CertificationMaster）
        jlpt_map: dict[str, CertificationMaster] = {}
        for c in cert_by_cat.get("LANGUAGE", []):
            for level in ["N1", "N2", "N3", "N4", "N5"]:
                if f"JLPT {level}" in c.name:
                    jlpt_map[level] = c

        # JLPT 以外の LANGUAGE 資格
        lang_non_jlpt = [c for c in cert_by_cat.get("LANGUAGE", []) if "JLPT" not in c.name]
        cloud_certs   = cert_by_cat.get("CLOUD", [])
        pm_certs      = cert_by_cat.get("PM", [])
        other_certs   = cert_by_cat.get("OTHER", [])
        network_certs = cert_by_cat.get("NETWORK", [])
        security_certs = cert_by_cat.get("SECURITY", [])

        print(f"  → 合計 {len(all_certs)} 件 "
              f"(LANGUAGE:{len(cert_by_cat.get('LANGUAGE',[]))}, "
              f"CLOUD:{len(cloud_certs)}, PM:{len(pm_certs)}, "
              f"NETWORK:{len(network_certs)}, SECURITY:{len(security_certs)}, "
              f"OTHER:{len(other_certs)})\n")

        # ── Step 4: admin 社員 ID を取得 ─────────────────────────────────
        print("🔑 [Step 4] admin ID 取得...")
        admin_res = await db.execute(
            select(Employee.id).where(Employee.system_role == "admin").limit(1)
        )
        admin_id: str | None = admin_res.scalar_one_or_none()
        if not admin_id:
            print("❌ admin 社員が見つかりません。先に `alembic upgrade head` を実行してください。")
            return
        print(f"  → {admin_id[:8]}...\n")

        # ── Step 5: 社員 1000 名を作成 ───────────────────────────────────
        print(f"👥 [Step 5] 社員 {TOTAL} 名を生成...")

        emp_list: list[tuple[Employee, int, str]] = []
        new_count = 0
        skip_count = 0

        for i in range(TOTAL):
            emp_num = f"EMP-{i + 1:04d}"
            ws_status = WORK_STATUS_WEIGHTS[i % len(WORK_STATUS_WEIGHTS)]

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

            user_id: str | None = None
            # member も emp0051〜emp0100 (i=50〜99) の50名はログイン可能にする
            has_account = role != "member" or (role == "member" and 50 <= i < 100)
            if has_account:
                emp_email = f"emp{i + 1:04d}@employeehub.local"
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

            if new_count % 100 == 0:
                await db.flush()
                print(f"  ... {new_count} 件作成済み")

        await db.flush()
        print(f"  → 新規作成: {new_count} 件 / スキップ（既存）: {skip_count} 件\n")

        # ── Step 5.5: member (i=50〜99) のうち user_id が未設定のものにアカウントを付与 ──
        print("🔑 [Step 5.5] member アカウント付与（emp0051〜emp0100）...")
        member_patched = 0
        for i in range(50, 100):
            emp_num = f"EMP-{i + 1:04d}"
            emp_ex = await db.execute(
                select(Employee).where(Employee.employee_number == emp_num)
            )
            emp = emp_ex.scalar_one_or_none()
            if emp is None or emp.user_id is not None:
                continue
            emp_email = f"emp{i + 1:04d}@employeehub.local"
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
            emp.user_id = user.id
            member_patched += 1
        await db.flush()
        print(f"  → {member_patched} 名にアカウント付与\n")

        # ── Step 6: スキル割り当て ─────────────────────────────────────────
        print("📚 [Step 6] スキル割り当て...")
        skill_total = 0
        processed = 0

        for emp, i, _ in emp_list:
            ex_sk = await db.execute(
                select(EmployeeSkill.id).where(EmployeeSkill.employee_id == emp.id).limit(1)
            )
            if ex_sk.scalar_one_or_none() is not None:
                processed += 1
                continue

            is_senior = (i % 10) < 6

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

        # ── Step 7: 資格割り当て ───────────────────────────────────────────
        print("🏅 [Step 7] 資格割り当て...")
        cert_total = 0
        cert_processed = 0

        for emp, i, _ in emp_list:
            # 冪等チェック
            ex_cert = await db.execute(
                select(EmployeeCertification.id)
                .where(EmployeeCertification.employee_id == emp.id)
                .limit(1)
            )
            if ex_cert.scalar_one_or_none() is not None:
                cert_processed += 1
                continue

            certs_to_assign: list[CertificationMaster] = []

            # (A) JLPT: ベトナム拠点社員は japanese_level に対応する JLPT を持ちやすい
            if emp.office_location in ("HANOI", "HCMC"):
                level = emp.japanese_level  # "N1".."N5" or "NONE"
                if level in jlpt_map and random.random() < 0.70:
                    certs_to_assign.append(jlpt_map[level])
                    # 1段階下のレベルも持っている場合
                    next_level = {"N1": "N2", "N2": "N3", "N3": "N4", "N4": "N5"}.get(level)
                    if next_level and next_level in jlpt_map and random.random() < 0.30:
                        certs_to_assign.append(jlpt_map[next_level])

            # (B) クラウド資格: 50% の確率
            if cloud_certs and random.random() < 0.50:
                certs_to_assign.append(random.choice(cloud_certs))
                # 30% でもう 1 件
                if random.random() < 0.30:
                    certs_to_assign.append(random.choice(cloud_certs))

            # (C) PM 資格: マネージャー/ディレクター/部門長は 45% の確率
            if pm_certs and emp.system_role in ("manager", "department_head", "director"):
                if random.random() < 0.45:
                    certs_to_assign.append(random.choice(pm_certs))

            # (D) TOEIC / プログラミング言語認定: 20% の確率
            if lang_non_jlpt and random.random() < 0.20:
                certs_to_assign.append(random.choice(lang_non_jlpt))

            # (E) インフラ・ネットワーク系: 15% の確率
            if network_certs and random.random() < 0.15:
                certs_to_assign.append(random.choice(network_certs))

            # (F) セキュリティ: 12% の確率
            if security_certs and random.random() < 0.12:
                certs_to_assign.append(random.choice(security_certs))

            # (G) ローコード / SaaS / DevOps (OTHER): 25% の確率
            if other_certs and random.random() < 0.25:
                certs_to_assign.append(random.choice(other_certs))

            # 重複を除去し最大 4 件に制限
            seen_ids: set[str] = set()
            unique_certs: list[CertificationMaster] = []
            for c in certs_to_assign:
                if c.id not in seen_ids:
                    seen_ids.add(c.id)
                    unique_certs.append(c)
            unique_certs = unique_certs[:4]

            # 資格レコードを生成
            for cert in unique_certs:
                status_roll = random.random()
                if status_roll < 0.70:
                    status = "APPROVED"
                elif status_roll < 0.85:
                    status = "PENDING"
                else:
                    status = "REJECTED"

                years_ago = random.randint(1, 4)
                obtained_at = date(2026 - years_ago, random.randint(1, 12), 15)

                # 有効期限計算
                expires_at = None
                if cert.has_expiry and status == "APPROVED":
                    # 10% → 60日以内期限切れ（Alert Dashboard テスト用）
                    if random.random() < 0.10:
                        expires_at = date(2026, 3, random.randint(5, 31))
                    else:
                        expire_year = obtained_at.year + 3
                        expires_at = date(expire_year, obtained_at.month, obtained_at.day)

                approver_id = admin_id if status in ("APPROVED", "REJECTED") else None
                approved_at = (
                    datetime.now(UTC) - timedelta(days=random.randint(1, 365))
                    if status in ("APPROVED", "REJECTED")
                    else None
                )

                db.add(EmployeeCertification(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    certification_master_id=cert.id,
                    custom_name=None,
                    score=None,
                    obtained_at=obtained_at,
                    expires_at=expires_at,
                    file_url=None,
                    status=status,
                    approver_id=approver_id,
                    approver_comment=None,
                    approved_at=approved_at,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                ))
                cert_total += 1

            cert_processed += 1
            if cert_processed % 200 == 0:
                await db.flush()
                print(f"  ... {cert_processed}/{len(emp_list)} 名処理 ({cert_total} 件)")

        await db.flush()
        print(f"  → 資格レコード: {cert_total} 件\n")

        # ── Step 8: 稼働状況 ───────────────────────────────────────────────
        print("📊 [Step 8] 稼働状況作成...")
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

        # ── Step 9: プロジェクトマスタ + アサイン ─────────────────────────
        print("📁 [Step 9] プロジェクト作成...")
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

        # ── Step 10: ビザ情報 ──────────────────────────────────────────────
        print("🛂 [Step 10] ビザ情報作成（HANOI/HCMC 拠点）...")
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

        # ── Step 11: プロジェクト経歴 ────────────────────────────────────────
        print("📁 [Step 11] プロジェクト経歴作成...")

        PROCESS_PHASES_ALL = [
            "要件定義", "基本設計", "詳細設計", "製造・実装",
            "単体テスト", "結合テスト", "総合テスト", "運用・保守",
        ]
        TECH_STACKS_POOL = [
            ["Java", "Spring Boot", "PostgreSQL", "Docker", "AWS"],
            ["Python", "FastAPI", "MySQL", "Redis", "GCP"],
            ["TypeScript", "React", "Node.js", "MongoDB", "Azure"],
            ["PHP", "Laravel", "MySQL", "Linux", "AWS"],
            ["C#", ".NET Core", "SQL Server", "Docker", "Azure"],
            ["Python", "Django", "PostgreSQL", "Nginx", "Linux"],
            ["TypeScript", "Vue.js", "PostgreSQL", "Docker", "AWS"],
            ["Java", "Spring MVC", "Oracle", "Linux", "VMware"],
            ["Kotlin", "Spring Boot", "MySQL", "Kubernetes", "GCP"],
            ["Python", "Flask", "MongoDB", "Redis", "AWS"],
        ]
        RESPONSIBILITIES_POOL = [
            "バックエンドAPIの設計・実装、DB設計、コードレビュー担当",
            "フロントエンド開発、ユニットテスト作成、CI/CD整備",
            "要件定義から詳細設計まで担当、クライアント折衝",
            "マイクロサービスアーキテクチャの設計、API仕様策定",
            "インフラ構築・運用、監視設定、障害対応",
            "QA計画立案、テスト仕様書作成、自動化テスト実装",
            "PMとして工程管理、メンバーマネジメント（3〜5名）",
            "データ分析基盤の設計・実装、ETLパイプライン構築",
            "モバイルアプリの機能開発、パフォーマンス改善",
            "セキュリティ診断、脆弱性対応、セキュリティ要件定義",
        ]
        LESSONS_POOL = [
            "大規模システムのDB設計とパフォーマンスチューニングを習得",
            "アジャイル開発のプロセスを経験し、スクラムの運用スキルを向上",
            "クラウドネイティブアーキテクチャの設計パターンを習得",
            "顧客折衝・要件定義の進め方を学び、コミュニケーション能力を向上",
            "CI/CDパイプラインの構築と自動テストの重要性を体得",
            "分散システムの設計原則とデータ一貫性の担保方法を学習",
            "大人数チームのリード経験でプロジェクト管理スキルを習得",
            "データパイプラインの設計とビッグデータ処理の知識を習得",
            "セキュアコーディングの実践とOWASP対応を経験",
            "マイクロサービスの運用ノウハウとKubernetesの実務スキルを習得",
        ]
        EP_ROLES = ["PL", "PM", "SE", "SE", "SE", "PG", "PG", "QA", "INFRA", "OTHER"]

        emp_proj_total = 0
        for emp, i, _ in emp_list:
            ex_ep = await db.execute(
                select(EmployeeProject.id).where(EmployeeProject.employee_id == emp.id).limit(1)
            )
            if ex_ep.scalar_one_or_none() is not None:
                continue

            num_projects = 1 + (i % 3)
            for j in range(num_projects):
                proj_template = project_objs[(i + j) % len(project_objs)]
                years_ago = 1 + j
                start_year = max(2018, 2025 - years_ago - (j // 2))
                start_month = (i * 3 + j * 7) % 12 + 1
                start_d = date(start_year, start_month, 1)

                if j == 0 and (i % 4 != 0):
                    end_d = None  # 最新PJは継続中が多い
                else:
                    end_year = min(2026, start_year + 1 + (i % 2))
                    end_month = (start_month + 6) % 12 + 1
                    end_d = date(end_year, end_month, 28)

                role = emp.system_role
                if role in ("manager", "department_head", "director"):
                    phases = random.sample(PROCESS_PHASES_ALL[:4], random.randint(2, 4))
                elif role == "sales":
                    phases = ["要件定義", "基本設計"]
                else:
                    phases = random.sample(PROCESS_PHASES_ALL[2:], random.randint(3, 6))

                if role in ("manager", "department_head"):
                    ep_role = random.choice(["PL", "PM"])
                else:
                    ep_role = EP_ROLES[(i + j) % len(EP_ROLES)]

                db.add(EmployeeProject(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    project_id=proj_template.id,
                    role=ep_role,
                    started_at=start_d,
                    ended_at=end_d,
                    tech_stack=TECH_STACKS_POOL[(i + j) % len(TECH_STACKS_POOL)],
                    team_size=random.choice([3, 5, 7, 10, 15]),
                    responsibilities=RESPONSIBILITIES_POOL[(i + j) % len(RESPONSIBILITIES_POOL)],
                    achievements=f"プロジェクトを予定通り納品。工数削減 {random.randint(10, 30)}%を達成",
                    process_phases=phases,
                    lessons_learned=LESSONS_POOL[(i + j) % len(LESSONS_POOL)],
                    sort_order=j,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                ))
                emp_proj_total += 1

            if emp_proj_total % 300 == 0:
                await db.flush()

        await db.flush()
        print(f"  → プロジェクト経歴: {emp_proj_total} 件\n")

        # ── 最終コミット ──────────────────────────────────────────────────
        await db.commit()

        print("=" * 55)
        print("✅  Bulk Seed 完了!")
        print(f"   社員:        {len(emp_list):>5} 名（新規: {new_count}）")
        print(f"   スキル:      {skill_total:>5} 件")
        print(f"   資格:        {cert_total:>5} 件")
        print(f"   稼働状況:    {ws_total:>5} 件")
        print(f"   アサイン:    {asgn_total:>5} 件")
        print(f"   ビザ情報:    {visa_total:>5} 件")
        print(f"   PJ経歴:      {emp_proj_total:>5} 件")
        print("=" * 55)
        print("\n🌐 確認:")
        print("   http://localhost:3000  →  admin@employeehub.local / Admin1234!")
        print("   manager (0001〜0020)   →  emp0001〜emp0020@employeehub.local / Test1234!")
        print("   dept_head (0021〜0030) →  emp0021〜emp0030@employeehub.local / Test1234!")
        print("   sales (0031〜0045)     →  emp0031〜emp0045@employeehub.local / Test1234!")
        print("   director (0046〜0050)  →  emp0046〜emp0050@employeehub.local / Test1234!")
        print("   member (0051〜0100)    →  emp0051〜emp0100@employeehub.local / Test1234!")


if __name__ == "__main__":
    asyncio.run(seed())
