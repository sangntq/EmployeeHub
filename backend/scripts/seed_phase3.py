"""
Phase 3 デモデータ投入スクリプト

実行方法:
  docker compose exec backend python scripts/seed_phase3.py
"""
import sys, os, uuid, asyncio
sys.path.insert(0, "/app")

from datetime import date, datetime, UTC
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, text

from app.core.config import settings
from app.models.employee import Employee
from app.models.project import Project, EmployeeProject, VisaInfo
from app.models.work_status import WorkStatus, Assignment

DATABASE_URL = settings.DATABASE_URL


async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as db:
        # 既存の社員を取得
        result = await db.execute(select(Employee).where(Employee.is_active == True).limit(5))
        employees = list(result.scalars().all())

        if not employees:
            print("❌ 社員データが見つかりません。先に alembic upgrade head を実行してください。")
            return

        print(f"✅ {len(employees)} 名の社員を取得")

        # ── プロジェクトマスタ ────────────────────────────────────────────
        projects_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "ECサイトリニューアル",
                "client_name": "株式会社サンプル商事",
                "industry": "EC・小売",
                "started_at": date(2024, 4, 1),
                "ended_at": date(2025, 3, 31),
                "created_at": datetime.now(UTC),
            },
            {
                "id": str(uuid.uuid4()),
                "name": "基幹システム刷新PJ",
                "client_name": "ABC製造株式会社",
                "industry": "製造業",
                "started_at": date(2025, 1, 1),
                "ended_at": None,
                "created_at": datetime.now(UTC),
            },
            {
                "id": str(uuid.uuid4()),
                "name": "モバイルアプリ開発",
                "client_name": "XYZフィンテック",
                "industry": "金融",
                "started_at": date(2023, 7, 1),
                "ended_at": date(2024, 6, 30),
                "created_at": datetime.now(UTC),
            },
        ]

        proj_objs = []
        for pd in projects_data:
            # 既存チェック
            ex = await db.execute(select(Project).where(Project.name == pd["name"]))
            p = ex.scalar_one_or_none()
            if p is None:
                p = Project(**pd, created_by=employees[0].id)
                db.add(p)
                await db.flush()
                print(f"  📁 プロジェクト作成: {p.name}")
            proj_objs.append(p)

        # ── 各社員にデータを投入 ─────────────────────────────────────────

        statuses = ["ASSIGNED", "FREE_IMMEDIATE", "FREE_PLANNED", "INTERNAL", "LEAVE"]
        roles = ["PL", "SE", "PG", "QA", "INFRA"]
        tech_stacks = [
            ["Java", "Spring Boot", "PostgreSQL", "AWS"],
            ["React", "TypeScript", "FastAPI", "Docker"],
            ["Python", "Django", "MySQL", "GCP"],
            ["Vue.js", "Node.js", "MongoDB"],
            ["Kotlin", "Android", "Firebase"],
        ]

        for i, emp in enumerate(employees):
            # 稼働状況
            ex = await db.execute(select(WorkStatus).where(WorkStatus.employee_id == emp.id))
            ws = ex.scalar_one_or_none()
            if ws is None:
                ws = WorkStatus(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    status=statuses[i % len(statuses)],
                    free_from=date(2026, 4, 1) if statuses[i % len(statuses)] == "FREE_PLANNED" else None,
                    note=f"{emp.name_ja} のサンプル稼働状況",
                    updated_by=employees[0].id,
                    updated_at=datetime.now(UTC),
                )
                db.add(ws)
                print(f"  📊 稼働状況設定: {emp.name_ja} → {ws.status}")

            # プロジェクト経歴（1〜2件）
            ex_proj = await db.execute(select(EmployeeProject).where(EmployeeProject.employee_id == emp.id))
            existing_projs = list(ex_proj.scalars().all())
            if not existing_projs:
                # 1件目
                ep1 = EmployeeProject(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    project_id=proj_objs[i % len(proj_objs)].id,
                    role=roles[i % len(roles)],
                    started_at=proj_objs[i % len(proj_objs)].started_at or date(2024, 1, 1),
                    ended_at=proj_objs[i % len(proj_objs)].ended_at,
                    tech_stack=tech_stacks[i % len(tech_stacks)],
                    team_size=5 + (i * 2),
                    responsibilities=f"バックエンドAPI設計・実装、コードレビュー担当",
                    achievements=f"レスポンスタイムを30%改善、バグ件数を月平均5件以下に低減",
                    sort_order=0,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
                db.add(ep1)

                # 2件目（最初の社員以外に追加）
                if i > 0:
                    proj2 = proj_objs[(i + 1) % len(proj_objs)]
                    ep2 = EmployeeProject(
                        id=str(uuid.uuid4()),
                        employee_id=emp.id,
                        project_id=proj2.id,
                        role="SE",
                        started_at=date(2023, 1, 1),
                        ended_at=date(2023, 12, 31),
                        tech_stack=["Java", "MySQL", "Linux"],
                        team_size=10,
                        responsibilities="サーバーサイド実装",
                        achievements="新機能リリースを3ヶ月前倒しで達成",
                        sort_order=1,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                    db.add(ep2)

                print(f"  📋 プロジェクト経歴追加: {emp.name_ja}")

            # ビザ情報（海外拠点の社員に設定）
            if emp.office_location in ("HANOI", "HCMC"):
                ex_visa = await db.execute(select(VisaInfo).where(VisaInfo.employee_id == emp.id))
                vi = ex_visa.scalar_one_or_none()
                if vi is None:
                    vi = VisaInfo(
                        id=str(uuid.uuid4()),
                        employee_id=emp.id,
                        visa_type="技術・人文知識・国際業務",
                        residence_card_number=f"AB{i+1:07d}CD",
                        expires_at=date(2027, 3, 31) if i % 2 == 0 else date(2026, 6, 30),
                        notes="在留カード更新済み" if i % 2 == 0 else "更新申請中（2026年5月期限）",
                        updated_by=employees[0].id,
                        updated_at=datetime.now(UTC),
                    )
                    db.add(vi)
                    print(f"  🛂 ビザ情報追加: {emp.name_ja} (期限: {vi.expires_at})")

            # アサイン情報（ASSIGNED / FREE_PLANNEDの社員に）
            if statuses[i % len(statuses)] in ("ASSIGNED", "FREE_PLANNED"):
                ex_asgn = await db.execute(select(Assignment).where(Assignment.employee_id == emp.id))
                existing_asgn = list(ex_asgn.scalars().all())
                if not existing_asgn:
                    asgn = Assignment(
                        id=str(uuid.uuid4()),
                        employee_id=emp.id,
                        project_id=proj_objs[i % len(proj_objs)].id,
                        allocation_percent=80 if i % 2 == 0 else 100,
                        started_at=date(2025, 10, 1),
                        ends_at=date(2026, 6, 30),
                        is_active=True,
                        created_by=employees[0].id,
                        created_at=datetime.now(UTC),
                    )
                    db.add(asgn)
                    print(f"  🔗 アサイン追加: {emp.name_ja} → {proj_objs[i % len(proj_objs)].name}")

        await db.commit()
        print("\n✅ Phase 3 サンプルデータ投入完了!")
        print("   → http://localhost:3000 でログインして確認してください")
        print("   → 社員詳細 → 稼働状況 / プロジェクト経歴 / ビザタブを確認")


if __name__ == "__main__":
    asyncio.run(seed())
