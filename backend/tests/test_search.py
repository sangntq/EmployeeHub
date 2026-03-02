"""
Phase 4: 検索・マッチング APIテスト

- POST /search/filter  : 複合フィルター検索
- GET  /search/saved   : 保存済み検索一覧
- POST /search/saved   : 検索条件保存
- DELETE /search/saved/{id}: 保存済み検索削除
"""
import uuid
import pytest
from datetime import date, datetime, UTC

from app.core.security import create_access_token
from app.models.employee import Employee
from app.models.skill import SkillCategory, Skill, EmployeeSkill
from app.models.work_status import WorkStatus
from sqlalchemy.ext.asyncio import AsyncSession


# ── 追加フィクスチャ ────────────────────────────────────────────────────────────

@pytest.fixture
async def skill_category(db: AsyncSession) -> SkillCategory:
    cat = SkillCategory(
        id=str(uuid.uuid4()),
        name_ja="プログラミング",
        name_en="Programming",
        sort_order=1,
    )
    db.add(cat)
    await db.flush()
    return cat


@pytest.fixture
async def skill_java(db: AsyncSession, skill_category: SkillCategory) -> Skill:
    skill = Skill(
        id=str(uuid.uuid4()),
        category_id=skill_category.id,
        name="Java",
        name_ja="Java",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db.add(skill)
    await db.flush()
    return skill


@pytest.fixture
async def skill_python(db: AsyncSession, skill_category: SkillCategory) -> Skill:
    skill = Skill(
        id=str(uuid.uuid4()),
        category_id=skill_category.id,
        name="Python",
        name_ja="Python",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db.add(skill)
    await db.flush()
    return skill


@pytest.fixture
async def admin_with_java(
    db: AsyncSession, admin_employee: Employee, skill_java: Skill
) -> EmployeeSkill:
    """admin社員に承認済みJavaスキル(level=3)を付与する。"""
    es = EmployeeSkill(
        id=str(uuid.uuid4()),
        employee_id=admin_employee.id,
        skill_id=skill_java.id,
        self_level=3,
        approved_level=3,
        status="APPROVED",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(es)
    await db.flush()
    return es


@pytest.fixture
async def admin_work_status_assigned(
    db: AsyncSession, admin_employee: Employee
) -> WorkStatus:
    ws = WorkStatus(
        id=str(uuid.uuid4()),
        employee_id=admin_employee.id,
        status="ASSIGNED",
        updated_at=datetime.now(UTC),
    )
    db.add(ws)
    await db.flush()
    return ws


@pytest.fixture
def member_headers(member_employee: Employee) -> dict:
    """memberロール用認証ヘッダー。"""
    token = create_access_token(
        subject=member_employee.id,
        extra={"role": member_employee.system_role},
    )
    return {"Authorization": f"Bearer {token}"}


# ── フィルター検索テスト ─────────────────────────────────────────────────────────

class TestSearchFilter:

    async def test_search_no_filter_returns_all_active(
        self, client, auth_headers, admin_employee, member_employee
    ):
        """フィルターなしで全アクティブ社員を返す。"""
        resp = await client.post("/api/v1/search/filter", json={}, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert len(data["items"]) == 2

    async def test_search_inactive_excluded(
        self, client, auth_headers, admin_employee, db: AsyncSession
    ):
        """非アクティブ社員は検索結果に含まれない。"""
        inactive = Employee(
            id=str(uuid.uuid4()),
            employee_number="TEST-999",
            name_ja="非アクティブ社員",
            system_role="member",
            office_location="HANOI",
            employment_type="FULLTIME",
            work_style="ONSITE",
            joined_at=date(2024, 1, 1),
            email="inactive@test.local",
            is_active=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(inactive)
        await db.flush()

        resp = await client.post("/api/v1/search/filter", json={}, headers=auth_headers)
        assert resp.status_code == 200
        ids = [item["employee"]["id"] for item in resp.json()["items"]]
        assert inactive.id not in ids

    async def test_search_filter_office_location(
        self, client, auth_headers, admin_employee, member_employee
    ):
        """拠点フィルター: HANOI → adminのみ返る（memberはHCMC）。"""
        resp = await client.post(
            "/api/v1/search/filter",
            json={"office_locations": ["HANOI"]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["employee"]["id"] == admin_employee.id

    async def test_search_filter_work_style(
        self, client, auth_headers, admin_employee, member_employee
    ):
        """勤務スタイルフィルター: REMOTE → adminのみ返る（memberはONSITE）。"""
        resp = await client.post(
            "/api/v1/search/filter",
            json={"work_style": "REMOTE"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["employee"]["id"] == admin_employee.id

    async def test_search_filter_work_status(
        self, client, auth_headers,
        admin_work_status_assigned, admin_employee, member_employee
    ):
        """稼働状況フィルター: ASSIGNED → WorkStatus=ASSIGNEDのadminのみ返る。"""
        resp = await client.post(
            "/api/v1/search/filter",
            json={"work_statuses": ["ASSIGNED"]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["employee"]["id"] == admin_employee.id

    async def test_search_filter_japanese_level(
        self, client, auth_headers, admin_employee, db: AsyncSession
    ):
        """日本語レベルフィルター: N2以上 → N2/N1/NATIVE社員のみ返る。"""
        # N1社員を追加
        emp_n1 = Employee(
            id=str(uuid.uuid4()),
            employee_number="TEST-101",
            name_ja="N1社員",
            system_role="member",
            office_location="TOKYO",
            employment_type="FULLTIME",
            work_style="ONSITE",
            joined_at=date(2024, 1, 1),
            email="n1@test.local",
            is_active=True,
            japanese_level="N1",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        # N3社員を追加（N2未満 → 除外される）
        emp_n3 = Employee(
            id=str(uuid.uuid4()),
            employee_number="TEST-102",
            name_ja="N3社員",
            system_role="member",
            office_location="HANOI",
            employment_type="FULLTIME",
            work_style="ONSITE",
            joined_at=date(2024, 1, 1),
            email="n3@test.local",
            is_active=True,
            japanese_level="N3",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(emp_n1)
        db.add(emp_n3)
        await db.flush()

        resp = await client.post(
            "/api/v1/search/filter",
            json={"japanese_level": "N2"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        result_ids = {item["employee"]["id"] for item in resp.json()["items"]}
        assert emp_n1.id in result_ids
        assert emp_n3.id not in result_ids

    async def test_search_required_skill_filters_employees(
        self, client, auth_headers,
        admin_with_java, admin_employee, member_employee, skill_java
    ):
        """必須スキルフィルター: Javaを保持しないmemberは返らない。"""
        resp = await client.post(
            "/api/v1/search/filter",
            json={"skills": [{"skill_id": skill_java.id, "required": True}]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["employee"]["id"] == admin_employee.id

    async def test_search_required_skill_level_min(
        self, client, auth_headers,
        admin_with_java, admin_employee, skill_java
    ):
        """level_min=4: adminのapproved_level=3は条件未満 → 0件。"""
        resp = await client.post(
            "/api/v1/search/filter",
            json={"skills": [{"skill_id": skill_java.id, "required": True, "level_min": 4}]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


# ── マッチスコアテスト ──────────────────────────────────────────────────────────

class TestMatchScore:

    async def test_score_100_when_no_skill_criteria(
        self, client, auth_headers, admin_employee
    ):
        """スキル条件なし → base_score=80 + bonus=20 = 100。"""
        resp = await client.post("/api/v1/search/filter", json={}, headers=auth_headers)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["match_score"] == 100

    async def test_score_partial_optional_match(
        self, client, auth_headers,
        admin_with_java, admin_employee, skill_java, skill_python
    ):
        """任意スキル2件中1件マッチ → bonus=int(1/2×20)=10 → score=90。"""
        resp = await client.post(
            "/api/v1/search/filter",
            json={
                "skills": [
                    {"skill_id": skill_java.id, "required": False},
                    {"skill_id": skill_python.id, "required": False},
                ]
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        admin_item = next(
            item for item in resp.json()["items"]
            if item["employee"]["id"] == admin_employee.id
        )
        # base=80（必須スキルなし）, optional 1/2 matched → bonus=10, score=90
        assert admin_item["match_score"] == 90

    async def test_score_optional_full_match(
        self, client, auth_headers,
        admin_with_java, admin_employee, skill_java
    ):
        """任意スキル1件マッチ → bonus=20 → score=100。"""
        resp = await client.post(
            "/api/v1/search/filter",
            json={
                "skills": [{"skill_id": skill_java.id, "required": False}]
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        admin_item = next(
            item for item in resp.json()["items"]
            if item["employee"]["id"] == admin_employee.id
        )
        # base=80, optional 1/1 matched → bonus=20, score=100
        assert admin_item["match_score"] == 100


# ── 保存済み検索テスト ──────────────────────────────────────────────────────────

class TestSavedSearch:

    async def test_saved_search_list_empty(self, client, auth_headers, admin_employee):
        """保存済み検索なし → 空リスト。"""
        resp = await client.get("/api/v1/search/saved", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_saved_search_create_and_list(self, client, auth_headers, admin_employee):
        """保存済み検索の作成と一覧取得。"""
        body = {"name": "HANOIエンジニア", "criteria": {"office_locations": ["HANOI"]}}
        create_resp = await client.post(
            "/api/v1/search/saved", json=body, headers=auth_headers
        )
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["name"] == "HANOIエンジニア"
        assert "id" in created
        assert created["criteria"]["office_locations"] == ["HANOI"]

        list_resp = await client.get("/api/v1/search/saved", headers=auth_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1
        assert list_resp.json()[0]["id"] == created["id"]

    async def test_saved_search_delete(self, client, auth_headers, admin_employee):
        """保存済み検索の削除後は一覧から消える。"""
        create_resp = await client.post(
            "/api/v1/search/saved",
            json={"name": "削除テスト", "criteria": {}},
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        search_id = create_resp.json()["id"]

        del_resp = await client.delete(
            f"/api/v1/search/saved/{search_id}", headers=auth_headers
        )
        assert del_resp.status_code == 204

        list_resp = await client.get("/api/v1/search/saved", headers=auth_headers)
        assert list_resp.json() == []


# ── RBAC テスト ─────────────────────────────────────────────────────────────────

class TestRBAC:

    async def test_member_cannot_search(
        self, client, member_headers, member_employee
    ):
        """memberロールは検索APIにアクセスできない → 403。"""
        resp = await client.post(
            "/api/v1/search/filter", json={}, headers=member_headers
        )
        assert resp.status_code == 403

    async def test_member_cannot_access_saved_search(
        self, client, member_headers, member_employee
    ):
        """memberロールは保存済み検索APIにもアクセスできない → 403。"""
        resp = await client.get("/api/v1/search/saved", headers=member_headers)
        assert resp.status_code == 403
