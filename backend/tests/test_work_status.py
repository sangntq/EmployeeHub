"""
Phase 3 テスト: 稼働状況・プロジェクト経歴・ビザ情報・アサイン管理
"""
import uuid
import pytest
from datetime import date, datetime, UTC
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.employee import Employee
from app.models.project import Project, EmployeeProject, VisaInfo
from app.models.work_status import WorkStatus, Assignment
from app.models.user import User
from app.core.security import hash_password


# ── フィクスチャ ────────────────────────────────────────────────────────────────

@pytest.fixture
async def manager_user(db: AsyncSession) -> User:
    user = User(
        id=str(uuid.uuid4()),
        email="manager@test.local",
        password_hash=hash_password("TestPass1!"),
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(user)
    await db.flush()
    return user


@pytest.fixture
async def manager_employee(db: AsyncSession, manager_user: User) -> Employee:
    emp = Employee(
        id=str(uuid.uuid4()),
        user_id=manager_user.id,
        employee_number="MGR-001",
        name_ja="テストマネージャー",
        name_en="Test Manager",
        system_role="manager",
        office_location="HANOI",
        employment_type="FULLTIME",
        work_style="REMOTE",
        joined_at=date(2023, 1, 1),
        email=manager_user.email,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(emp)
    await db.flush()
    return emp


@pytest.fixture
def manager_token(manager_employee: Employee) -> str:
    return create_access_token(
        subject=manager_employee.id,
        extra={"role": manager_employee.system_role},
    )


@pytest.fixture
def manager_headers(manager_token: str) -> dict:
    return {"Authorization": f"Bearer {manager_token}"}


@pytest.fixture
async def sample_project(db: AsyncSession, admin_employee: Employee) -> Project:
    proj = Project(
        id=str(uuid.uuid4()),
        name="テストプロジェクト",
        client_name="株式会社テスト",
        industry="IT",
        started_at=date(2025, 1, 1),
        created_by=admin_employee.id,
        created_at=datetime.now(UTC),
    )
    db.add(proj)
    await db.flush()
    return proj


@pytest.fixture
async def work_status_record(db: AsyncSession, member_employee: Employee) -> WorkStatus:
    ws = WorkStatus(
        id=str(uuid.uuid4()),
        employee_id=member_employee.id,
        status="ASSIGNED",
        note="現在アサイン中",
        updated_at=datetime.now(UTC),
    )
    db.add(ws)
    await db.flush()
    return ws


@pytest.fixture
async def emp_project(db: AsyncSession, member_employee: Employee, sample_project: Project) -> EmployeeProject:
    ep = EmployeeProject(
        id=str(uuid.uuid4()),
        employee_id=member_employee.id,
        project_id=sample_project.id,
        role="SE",
        started_at=date(2025, 1, 1),
        tech_stack=["Java", "Spring Boot"],
        team_size=5,
        sort_order=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(ep)
    await db.flush()
    return ep


@pytest.fixture
async def visa_record(db: AsyncSession, member_employee: Employee) -> VisaInfo:
    vi = VisaInfo(
        id=str(uuid.uuid4()),
        employee_id=member_employee.id,
        visa_type="技術・人文知識・国際業務",
        expires_at=date(2027, 3, 31),
        updated_at=datetime.now(UTC),
    )
    db.add(vi)
    await db.flush()
    return vi


# ── 稼働状況 ────────────────────────────────────────────────────────────────────

class TestGetWorkStatus:
    async def test_get_work_status_not_exists(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee
    ):
        """存在しない場合は FREE_IMMEDIATE で新規作成して返す。"""
        resp = await client.get(
            f"/api/v1/employees/{member_employee.id}/work-status",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "FREE_IMMEDIATE"

    async def test_get_work_status_exists(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee,
        work_status_record: WorkStatus,
    ):
        """既存レコードが返る。"""
        resp = await client.get(
            f"/api/v1/employees/{member_employee.id}/work-status",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ASSIGNED"

    async def test_get_work_status_unauthenticated(
        self, client: AsyncClient, member_employee: Employee
    ):
        resp = await client.get(f"/api/v1/employees/{member_employee.id}/work-status")
        assert resp.status_code in (401, 403)  # HTTPBearer returns 403 when no token


class TestUpdateWorkStatus:
    async def test_manager_can_update(
        self, client: AsyncClient, manager_headers: dict,
        member_employee: Employee,
    ):
        """manager は稼働状況を更新できる。"""
        resp = await client.patch(
            f"/api/v1/employees/{member_employee.id}/work-status",
            headers=manager_headers,
            json={"status": "FREE_PLANNED", "free_from": "2026-04-01", "note": "案件終了予定"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "FREE_PLANNED"
        assert data["free_from"] == "2026-04-01"
        assert data["note"] == "案件終了予定"

    async def test_member_cannot_update(
        self, client: AsyncClient, member_employee: Employee, db: AsyncSession
    ):
        """member は稼働状況を更新できない。"""
        member_token = create_access_token(
            subject=member_employee.id,
            extra={"role": member_employee.system_role},
        )
        resp = await client.patch(
            f"/api/v1/employees/{member_employee.id}/work-status",
            headers={"Authorization": f"Bearer {member_token}"},
            json={"status": "FREE_IMMEDIATE"},
        )
        assert resp.status_code == 403

    async def test_admin_can_update(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee,
    ):
        """admin は稼働状況を更新できる。"""
        resp = await client.patch(
            f"/api/v1/employees/{member_employee.id}/work-status",
            headers=auth_headers,
            json={"status": "INTERNAL", "note": "社内業務"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "INTERNAL"


# ── プロジェクト経歴 ─────────────────────────────────────────────────────────────

class TestListEmployeeProjects:
    async def test_list_empty(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee
    ):
        resp = await client.get(
            f"/api/v1/employees/{member_employee.id}/projects",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_with_records(
        self, client: AsyncClient, auth_headers: dict,
        member_employee: Employee, emp_project: EmployeeProject,
    ):
        resp = await client.get(
            f"/api/v1/employees/{member_employee.id}/projects",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["role"] == "SE"
        assert data[0]["tech_stack"] == ["Java", "Spring Boot"]


class TestAddEmployeeProject:
    async def test_add_project(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee
    ):
        """admin が社員のプロジェクト経歴を追加できる。"""
        resp = await client.post(
            f"/api/v1/employees/{member_employee.id}/projects",
            headers=auth_headers,
            json={
                "project_name": "ECサイト開発",
                "client_name": "株式会社サンプル",
                "industry": "EC",
                "role": "PL",
                "started_at": "2024-04-01",
                "ended_at": "2025-03-31",
                "tech_stack": ["React", "FastAPI", "PostgreSQL"],
                "team_size": 8,
                "responsibilities": "フロントエンド設計",
                "achievements": "レスポンスタイム50%改善",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["role"] == "PL"
        assert data["project"]["name"] == "ECサイト開発"
        assert data["tech_stack"] == ["React", "FastAPI", "PostgreSQL"]

    async def test_member_adds_own_project(
        self, client: AsyncClient, member_employee: Employee
    ):
        """member は自分のプロジェクト経歴を追加できる。"""
        member_token = create_access_token(
            subject=member_employee.id,
            extra={"role": member_employee.system_role},
        )
        resp = await client.post(
            f"/api/v1/employees/{member_employee.id}/projects",
            headers={"Authorization": f"Bearer {member_token}"},
            json={
                "project_name": "個人プロジェクト",
                "role": "SE",
                "started_at": "2024-01-01",
                "tech_stack": ["Python"],
            },
        )
        assert resp.status_code == 201

    async def test_member_cannot_add_others_project(
        self, client: AsyncClient, member_employee: Employee, admin_employee: Employee
    ):
        """member は他人のプロジェクト経歴を追加できない。"""
        member_token = create_access_token(
            subject=member_employee.id,
            extra={"role": member_employee.system_role},
        )
        resp = await client.post(
            f"/api/v1/employees/{admin_employee.id}/projects",
            headers={"Authorization": f"Bearer {member_token}"},
            json={
                "project_name": "テスト",
                "role": "SE",
                "started_at": "2024-01-01",
            },
        )
        assert resp.status_code == 403


class TestUpdateDeleteProject:
    async def test_update_project(
        self, client: AsyncClient, auth_headers: dict,
        emp_project: EmployeeProject,
    ):
        resp = await client.put(
            f"/api/v1/employee-projects/{emp_project.id}",
            headers=auth_headers,
            json={"tech_stack": ["Java", "Spring Boot", "Kubernetes"]},
        )
        assert resp.status_code == 200
        assert "Kubernetes" in resp.json()["tech_stack"]

    async def test_delete_project(
        self, client: AsyncClient, auth_headers: dict,
        emp_project: EmployeeProject, member_employee: Employee,
    ):
        resp = await client.delete(
            f"/api/v1/employee-projects/{emp_project.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

        # 削除後に一覧から消えていることを確認
        resp2 = await client.get(
            f"/api/v1/employees/{member_employee.id}/projects",
            headers=auth_headers,
        )
        assert resp2.json() == []


# ── ビザ情報 ──────────────────────────────────────────────────────────────────

class TestVisaInfo:
    async def test_get_visa_not_exists(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee
    ):
        resp = await client.get(
            f"/api/v1/employees/{member_employee.id}/visa",
            headers=auth_headers,
        )
        # 存在しない場合は null を返す
        assert resp.status_code == 200
        assert resp.json() is None

    async def test_upsert_visa(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee
    ):
        """admin はビザ情報を作成できる。"""
        resp = await client.put(
            f"/api/v1/employees/{member_employee.id}/visa",
            headers=auth_headers,
            json={
                "visa_type": "技術・人文知識・国際業務",
                "residence_card_number": "AB12345678CD",
                "expires_at": "2027-03-31",
                "notes": "更新申請中",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["visa_type"] == "技術・人文知識・国際業務"
        assert data["expires_at"] == "2027-03-31"

    async def test_update_existing_visa(
        self, client: AsyncClient, auth_headers: dict,
        member_employee: Employee, visa_record: VisaInfo,
    ):
        """既存ビザ情報を更新できる。"""
        resp = await client.put(
            f"/api/v1/employees/{member_employee.id}/visa",
            headers=auth_headers,
            json={"expires_at": "2028-01-01", "notes": "更新済み"},
        )
        assert resp.status_code == 200
        assert resp.json()["expires_at"] == "2028-01-01"

    async def test_member_cannot_access_others_visa(
        self, client: AsyncClient, member_employee: Employee, admin_employee: Employee
    ):
        """member は他人のビザ情報を閲覧できない。"""
        member_token = create_access_token(
            subject=member_employee.id,
            extra={"role": member_employee.system_role},
        )
        resp = await client.get(
            f"/api/v1/employees/{admin_employee.id}/visa",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resp.status_code == 403

    async def test_member_cannot_update_visa(
        self, client: AsyncClient, member_employee: Employee
    ):
        """member はビザ情報を更新できない。"""
        member_token = create_access_token(
            subject=member_employee.id,
            extra={"role": member_employee.system_role},
        )
        resp = await client.put(
            f"/api/v1/employees/{member_employee.id}/visa",
            headers={"Authorization": f"Bearer {member_token}"},
            json={"visa_type": "留学"},
        )
        assert resp.status_code == 403


# ── アサイン管理 ─────────────────────────────────────────────────────────────────

class TestAssignments:
    async def test_list_empty(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee
    ):
        resp = await client.get(
            f"/api/v1/employees/{member_employee.id}/assignments",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_create_assignment(
        self, client: AsyncClient, manager_headers: dict,
        member_employee: Employee, sample_project: Project,
    ):
        """manager はアサインを登録できる。"""
        resp = await client.post(
            f"/api/v1/employees/{member_employee.id}/assignments",
            headers=manager_headers,
            json={
                "project_id": sample_project.id,
                "allocation_percent": 80,
                "started_at": "2026-03-01",
                "ends_at": "2026-06-30",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["allocation_percent"] == 80
        assert data["project_name"] == "テストプロジェクト"

    async def test_member_cannot_create_assignment(
        self, client: AsyncClient, member_employee: Employee, sample_project: Project
    ):
        """member はアサインを登録できない。"""
        member_token = create_access_token(
            subject=member_employee.id,
            extra={"role": member_employee.system_role},
        )
        resp = await client.post(
            f"/api/v1/employees/{member_employee.id}/assignments",
            headers={"Authorization": f"Bearer {member_token}"},
            json={
                "project_id": sample_project.id,
                "allocation_percent": 100,
                "started_at": "2026-03-01",
            },
        )
        assert resp.status_code == 403
