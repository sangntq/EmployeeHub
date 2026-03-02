"""
Phase 6 ダッシュボード API テスト

- GET /api/v1/dashboard/overview
- GET /api/v1/dashboard/utilization-trend
- GET /api/v1/dashboard/free-forecast
- GET /api/v1/dashboard/skills-distribution
- GET /api/v1/alerts
"""
import pytest
import uuid
from datetime import date, datetime, timedelta, UTC

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.employee import Employee
from app.models.skill import Skill, SkillCategory, EmployeeSkill
from app.models.certification import EmployeeCertification, CertificationMaster
from app.models.work_status import WorkStatus
from app.models.project import VisaInfo


# ── ローカルフィクスチャ ──────────────────────────────────────────────────────

@pytest.fixture
async def manager_employee(db: AsyncSession) -> Employee:
    emp = Employee(
        id=str(uuid.uuid4()),
        employee_number="TEST-MGR",
        name_ja="テストマネージャー",
        name_en="Test Manager",
        system_role="manager",
        office_location="HANOI",
        employment_type="FULLTIME",
        work_style="REMOTE",
        joined_at=date(2024, 1, 1),
        email="manager@test.local",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(emp)
    await db.flush()
    return emp


@pytest.fixture
def manager_headers(manager_employee: Employee) -> dict:
    token = create_access_token(
        subject=manager_employee.id,
        extra={"role": manager_employee.system_role},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def sales_employee(db: AsyncSession) -> Employee:
    emp = Employee(
        id=str(uuid.uuid4()),
        employee_number="TEST-SALES",
        name_ja="テスト営業",
        name_en="Test Sales",
        system_role="sales",
        office_location="TOKYO",
        employment_type="FULLTIME",
        work_style="HYBRID",
        joined_at=date(2024, 1, 1),
        email="sales@test.local",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(emp)
    await db.flush()
    return emp


@pytest.fixture
def sales_headers(sales_employee: Employee) -> dict:
    token = create_access_token(
        subject=sales_employee.id,
        extra={"role": sales_employee.system_role},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def member_headers(member_employee: Employee) -> dict:
    token = create_access_token(
        subject=member_employee.id,
        extra={"role": member_employee.system_role},
    )
    return {"Authorization": f"Bearer {token}"}


# ── Overview テスト ─────────────────────────────────────────────────────────

class TestOverview:

    async def test_overview_200_admin(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        resp = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_employees" in data
        assert "assigned" in data
        assert "free_immediate" in data
        assert "free_planned" in data
        assert "utilization_rate" in data
        assert "pending_approvals" in data
        assert "alerts" in data

    async def test_overview_200_manager(self, client: AsyncClient, manager_employee: Employee, manager_headers: dict):
        resp = await client.get("/api/v1/dashboard/overview", headers=manager_headers)
        assert resp.status_code == 200

    async def test_overview_403_member(self, client: AsyncClient, member_employee: Employee, member_headers: dict):
        resp = await client.get("/api/v1/dashboard/overview", headers=member_headers)
        assert resp.status_code == 403

    async def test_overview_403_sales(self, client: AsyncClient, sales_employee: Employee, sales_headers: dict):
        resp = await client.get("/api/v1/dashboard/overview", headers=sales_headers)
        assert resp.status_code == 403

    async def test_overview_pending_approvals(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict, member_employee: Employee
    ):
        """PENDING スキル申請が pending_approvals にカウントされること。"""
        skill_cat = SkillCategory(
            id=str(uuid.uuid4()), name_ja="バックエンド", name_en="Backend", sort_order=1
        )
        db.add(skill_cat)
        skill = Skill(
            id=str(uuid.uuid4()), category_id=skill_cat.id, name="Java", is_active=True,
            created_at=datetime.now(UTC),
        )
        db.add(skill)
        es = EmployeeSkill(
            id=str(uuid.uuid4()),
            employee_id=member_employee.id,
            skill_id=skill.id,
            self_level=3,
            status="PENDING",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(es)
        await db.flush()

        resp = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["pending_approvals"] >= 1

    async def test_overview_visa_expiry_30d(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict, member_employee: Employee
    ):
        """ビザが30日以内に期限切れの場合、visa_expiry_30d にカウントされること。"""
        visa = VisaInfo(
            id=str(uuid.uuid4()),
            employee_id=member_employee.id,
            expires_at=date.today() + timedelta(days=15),
        )
        db.add(visa)
        await db.flush()

        resp = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["alerts"]["visa_expiry_30d"] >= 1

    async def test_overview_utilization_rate(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """稼働率 = assigned / total * 100 の計算が正しいこと。"""
        ws = WorkStatus(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            status="ASSIGNED",
            updated_at=datetime.now(UTC),
        )
        db.add(ws)
        await db.flush()

        resp = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        if data["total_employees"] > 0:
            expected = round(data["assigned"] / data["total_employees"] * 100, 1)
            assert data["utilization_rate"] == expected


# ── Utilization Trend テスト ─────────────────────────────────────────────────

class TestUtilizationTrend:

    async def test_trend_default_6_months(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        resp = await client.get("/api/v1/dashboard/utilization-trend", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["months"]) == 6

    async def test_trend_custom_3_months(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        resp = await client.get("/api/v1/dashboard/utilization-trend?months=3", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["months"]) == 3

    async def test_trend_403_member(self, client: AsyncClient, member_employee: Employee, member_headers: dict):
        resp = await client.get("/api/v1/dashboard/utilization-trend", headers=member_headers)
        assert resp.status_code == 403


# ── Free Forecast テスト ─────────────────────────────────────────────────────

class TestFreeForecast:

    async def test_forecast_returns_3_months(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        resp = await client.get("/api/v1/dashboard/free-forecast", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["forecast"]) == 3

    async def test_forecast_counts_free_planned(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """FREE_PLANNED のfree_from が来月以内ならforecastに加算されること。"""
        today = date.today()
        next_month = date(today.year + (today.month // 12), today.month % 12 + 1, 15)
        ws = WorkStatus(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            status="FREE_PLANNED",
            free_from=next_month,
            updated_at=datetime.now(UTC),
        )
        db.add(ws)
        await db.flush()

        resp = await client.get("/api/v1/dashboard/free-forecast", headers=auth_headers)
        assert resp.status_code == 200
        forecast = resp.json()["forecast"]
        # 2ヶ月目か3ヶ月目のfree_countが0より大きいはず
        assert any(m["free_count"] > 0 for m in forecast)


# ── Skills Distribution テスト ───────────────────────────────────────────────

class TestSkillsDistribution:

    async def test_skills_distribution_empty(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        resp = await client.get("/api/v1/dashboard/skills-distribution", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    async def test_skills_distribution_counts_free_engineers(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """フリーエンジニアの承認済みスキルが分布に含まれること。"""
        # フリー状態のWorkStatus
        ws = WorkStatus(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            status="FREE_IMMEDIATE",
            updated_at=datetime.now(UTC),
        )
        db.add(ws)
        # スキルマスタ
        cat = SkillCategory(id=str(uuid.uuid4()), name_ja="BE", name_en="Backend", sort_order=1)
        db.add(cat)
        skill = Skill(
            id=str(uuid.uuid4()), category_id=cat.id, name="Python", is_active=True,
            created_at=datetime.now(UTC),
        )
        db.add(skill)
        # 承認済みスキル
        es = EmployeeSkill(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            skill_id=skill.id,
            self_level=3,
            approved_level=3,
            status="APPROVED",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(es)
        await db.flush()

        resp = await client.get("/api/v1/dashboard/skills-distribution", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["skill_name"] == "Python"
        assert items[0]["free_count"] == 1


# ── Alerts テスト ────────────────────────────────────────────────────────────

class TestAlerts:

    async def test_alerts_visa_within_30d(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """30日以内に期限切れのビザがアラートに含まれること。"""
        visa = VisaInfo(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            expires_at=date.today() + timedelta(days=10),
        )
        db.add(visa)
        await db.flush()

        resp = await client.get("/api/v1/alerts", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        visa_items = [i for i in items if i["type"] == "VISA_EXPIRY"]
        assert len(visa_items) >= 1

    async def test_alerts_visa_outside_range_excluded(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """30日以降に期限切れのビザはデフォルト範囲に含まれないこと。"""
        visa = VisaInfo(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            expires_at=date.today() + timedelta(days=60),
        )
        db.add(visa)
        await db.flush()

        resp = await client.get("/api/v1/alerts", headers=auth_headers)
        assert resp.status_code == 200
        visa_items = [i for i in resp.json()["items"] if i["type"] == "VISA_EXPIRY"]
        assert len(visa_items) == 0

    async def test_alerts_cert_expiry(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """30日以内に期限切れの資格（APPROVED）がアラートに含まれること。"""
        master = CertificationMaster(
            id=str(uuid.uuid4()),
            name="AWS SAA",
            category="CLOUD",
            is_active=True,
        )
        db.add(master)
        cert = EmployeeCertification(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            certification_master_id=master.id,
            obtained_at=date(2023, 1, 1),
            expires_at=date.today() + timedelta(days=20),
            status="APPROVED",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(cert)
        await db.flush()

        resp = await client.get("/api/v1/alerts", headers=auth_headers)
        assert resp.status_code == 200
        cert_items = [i for i in resp.json()["items"] if i["type"] == "CERT_EXPIRY"]
        assert len(cert_items) >= 1

    async def test_alerts_type_filter_visa(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """type=VISA_EXPIRY フィルターでビザのみ返ること。"""
        visa = VisaInfo(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            expires_at=date.today() + timedelta(days=5),
        )
        db.add(visa)
        await db.flush()

        resp = await client.get("/api/v1/alerts?type=VISA_EXPIRY", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all(i["type"] == "VISA_EXPIRY" for i in items)

    async def test_alerts_custom_days(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """days=7 では7日以内のビザのみ返ること。"""
        # 5日後: 含まれる
        visa_in = VisaInfo(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            expires_at=date.today() + timedelta(days=5),
        )
        db.add(visa_in)
        await db.flush()

        resp = await client.get("/api/v1/alerts?days=7", headers=auth_headers)
        assert resp.status_code == 200
        visa_items = [i for i in resp.json()["items"] if i["type"] == "VISA_EXPIRY"]
        assert len(visa_items) >= 1

    async def test_alerts_403_member(self, client: AsyncClient, member_employee: Employee, member_headers: dict):
        resp = await client.get("/api/v1/alerts", headers=member_headers)
        assert resp.status_code == 403


# ── Skill Heatmap テスト ─────────────────────────────────────────────────────

class TestSkillHeatmap:

    async def test_heatmap_empty(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        """データなしの場合、空のリストを返すこと。"""
        resp = await client.get("/api/v1/dashboard/skill-heatmap", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "categories" in data
        assert "items" in data
        assert data["items"] == []

    async def test_heatmap_counts_approved_skills(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """APPROVED かつ approved_level が設定されているスキルがヒートマップに含まれること。"""
        cat = SkillCategory(id=str(uuid.uuid4()), name_ja="バックエンド", name_en="Backend", sort_order=1)
        db.add(cat)
        skill = Skill(
            id=str(uuid.uuid4()), category_id=cat.id, name="Go", is_active=True,
            created_at=datetime.now(UTC),
        )
        db.add(skill)
        es = EmployeeSkill(
            id=str(uuid.uuid4()),
            employee_id=admin_employee.id,
            skill_id=skill.id,
            self_level=3,
            approved_level=3,
            status="APPROVED",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(es)
        await db.flush()

        resp = await client.get("/api/v1/dashboard/skill-heatmap", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "バックエンド" in data["categories"]
        assert any(item["category"] == "バックエンド" and item["level"] == 3 and item["count"] >= 1
                   for item in data["items"])

    async def test_heatmap_403_member(self, client: AsyncClient, member_employee: Employee, member_headers: dict):
        resp = await client.get("/api/v1/dashboard/skill-heatmap", headers=member_headers)
        assert resp.status_code == 403


# ── Headcount Trend テスト ───────────────────────────────────────────────────

class TestHeadcountTrend:

    async def test_trend_default_12_months(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        """デフォルト12ヶ月分のデータを返すこと。"""
        resp = await client.get("/api/v1/dashboard/headcount-trend", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["months"]) == 12

    async def test_trend_joined_count(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """今月入社した社員がトレンドに反映されること。"""
        today = date.today()
        emp = Employee(
            id=str(uuid.uuid4()),
            employee_number="TEST-TREND-J",
            name_ja="トレンド入社",
            name_en="Trend Join",
            system_role="member",
            office_location="HANOI",
            employment_type="FULLTIME",
            work_style="REMOTE",
            joined_at=today,
            email="trendjoin@test.local",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(emp)
        await db.flush()

        resp = await client.get("/api/v1/dashboard/headcount-trend", headers=auth_headers)
        assert resp.status_code == 200
        months = resp.json()["months"]
        this_month = today.strftime("%Y-%m")
        month_data = next((m for m in months if m["month"] == this_month), None)
        assert month_data is not None
        assert month_data["joined"] >= 1

    async def test_trend_left_count(
        self, client: AsyncClient, db: AsyncSession, admin_employee: Employee, auth_headers: dict
    ):
        """今月退社した社員がトレンドに反映されること。"""
        today = date.today()
        emp = Employee(
            id=str(uuid.uuid4()),
            employee_number="TEST-TREND-L",
            name_ja="トレンド退社",
            name_en="Trend Left",
            system_role="member",
            office_location="HCMC",
            employment_type="FULLTIME",
            work_style="ONSITE",
            joined_at=date(2020, 1, 1),
            left_at=today,
            email="trendleft@test.local",
            is_active=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(emp)
        await db.flush()

        resp = await client.get("/api/v1/dashboard/headcount-trend", headers=auth_headers)
        assert resp.status_code == 200
        months = resp.json()["months"]
        this_month = today.strftime("%Y-%m")
        month_data = next((m for m in months if m["month"] == this_month), None)
        assert month_data is not None
        assert month_data["left"] >= 1

    async def test_trend_403_member(self, client: AsyncClient, member_employee: Employee, member_headers: dict):
        resp = await client.get("/api/v1/dashboard/headcount-trend", headers=member_headers)
        assert resp.status_code == 403


# ── Location Distribution テスト ─────────────────────────────────────────────

class TestLocationDistribution:

    async def test_location_distribution_200(
        self, client: AsyncClient, admin_employee: Employee, auth_headers: dict
    ):
        """在籍社員の拠点分布が返ること。"""
        resp = await client.get("/api/v1/dashboard/location-distribution", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        # admin_employee が在籍しているため1件以上返ること
        assert len(data["items"]) >= 1
        assert all("label" in item and "count" in item for item in data["items"])

    async def test_location_distribution_403_member(
        self, client: AsyncClient, member_employee: Employee, member_headers: dict
    ):
        resp = await client.get("/api/v1/dashboard/location-distribution", headers=member_headers)
        assert resp.status_code == 403
