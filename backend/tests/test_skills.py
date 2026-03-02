"""スキル・資格・承認キュー API テスト"""
import uuid
import pytest
from datetime import date, datetime, UTC
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.employee import Employee
from app.models.skill import SkillCategory, Skill, EmployeeSkill
from app.models.certification import CertificationMaster, EmployeeCertification
from tests.conftest import TestSessionLocal


# ── ヘルパーフィクスチャ ──────────────────────────────────────────────────────

@pytest.fixture
async def manager_employee(db: AsyncSession) -> Employee:
    """マネージャー社員を作成して返す。"""
    emp = Employee(
        id=str(uuid.uuid4()),
        user_id=None,
        employee_number="MGR-001",
        name_ja="テストマネージャー",
        name_en="Test Manager",
        system_role="manager",
        office_location="HANOI",
        employment_type="FULLTIME",
        work_style="REMOTE",
        joined_at=date(2023, 1, 1),
        email="manager@test.local",
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
async def skill_category(db: AsyncSession) -> SkillCategory:
    """テスト用スキルカテゴリを作成して返す。"""
    cat = SkillCategory(
        id=str(uuid.uuid4()),
        name_ja="プログラミング言語",
        name_en="Programming Language",
        sort_order=1,
    )
    db.add(cat)
    await db.flush()
    return cat


@pytest.fixture
async def skill(db: AsyncSession, skill_category: SkillCategory) -> Skill:
    """テスト用スキルを作成して返す。"""
    s = Skill(
        id=str(uuid.uuid4()),
        category_id=skill_category.id,
        name="Python",
        name_ja="Python",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db.add(s)
    await db.flush()
    return s


@pytest.fixture
async def cert_master(db: AsyncSession) -> CertificationMaster:
    """テスト用資格マスタを作成して返す。"""
    master = CertificationMaster(
        id=str(uuid.uuid4()),
        name="AWS Certified SAA",
        category="CLOUD",
        issuer="Amazon Web Services",
        has_expiry=True,
        is_active=True,
    )
    db.add(master)
    await db.flush()
    return master


@pytest.fixture
async def pending_skill(
    db: AsyncSession,
    member_employee: Employee,
    skill: Skill,
) -> EmployeeSkill:
    """PENDING 状態のスキル申請を作成して返す。"""
    now = datetime.now(UTC)
    es = EmployeeSkill(
        id=str(uuid.uuid4()),
        employee_id=member_employee.id,
        skill_id=skill.id,
        self_level=3,
        status="PENDING",
        created_at=now,
        updated_at=now,
    )
    db.add(es)
    await db.flush()
    return es


@pytest.fixture
async def pending_cert(
    db: AsyncSession,
    member_employee: Employee,
    cert_master: CertificationMaster,
) -> EmployeeCertification:
    """PENDING 状態の資格申請を作成して返す。"""
    now = datetime.now(UTC)
    ec = EmployeeCertification(
        id=str(uuid.uuid4()),
        employee_id=member_employee.id,
        certification_master_id=cert_master.id,
        obtained_at=date(2025, 1, 15),
        status="PENDING",
        created_at=now,
        updated_at=now,
    )
    db.add(ec)
    await db.flush()
    return ec


# ── スキルマスタ一覧 ──────────────────────────────────────────────────────────

class TestListSkills:
    async def test_list_skills_returns_categories(
        self, client: AsyncClient, auth_headers: dict, skill: Skill
    ):
        """認証済みユーザーがスキルマスタ一覧を取得できる。"""
        res = await client.get("/api/v1/skills", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "categories" in data
        assert len(data["categories"]) >= 1
        cat = data["categories"][0]
        assert cat["name_en"] == "Programming Language"
        assert len(cat["skills"]) >= 1
        assert cat["skills"][0]["name"] == "Python"

    async def test_list_skills_requires_auth(self, client: AsyncClient):
        """未認証アクセスは 403。"""
        res = await client.get("/api/v1/skills")
        assert res.status_code == 403

    async def test_list_skills_excludes_inactive(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, skill_category: SkillCategory
    ):
        """is_active=False のスキルは返さない。"""
        inactive = Skill(
            id=str(uuid.uuid4()),
            category_id=skill_category.id,
            name="OldLanguage",
            name_ja="古い言語",
            is_active=False,
            created_at=datetime.now(UTC),
        )
        db.add(inactive)
        await db.flush()

        res = await client.get("/api/v1/skills", headers=auth_headers)
        assert res.status_code == 200
        all_names = [
            s["name"]
            for cat in res.json()["categories"]
            for s in cat["skills"]
        ]
        assert "OldLanguage" not in all_names


# ── スキル申請 ────────────────────────────────────────────────────────────────

class TestApplySkill:
    async def test_apply_skill_success(
        self, client: AsyncClient, member_employee: Employee, skill: Skill
    ):
        """本人がスキルを申請できる。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"skill_id": skill.id, "self_level": 3, "self_comment": "実務経験2年"}
        res = await client.post(
            f"/api/v1/employees/{member_employee.id}/skills",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "PENDING"
        assert data["self_level"] == 3
        assert data["skill"]["name"] == "Python"

    async def test_apply_skill_forbidden_for_other(
        self, client: AsyncClient, member_employee: Employee, admin_employee: Employee, skill: Skill
    ):
        """他人のスキルは申請できない（403）。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"skill_id": skill.id, "self_level": 2}
        res = await client.post(
            f"/api/v1/employees/{admin_employee.id}/skills",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 403

    async def test_apply_skill_not_found(
        self, client: AsyncClient, member_employee: Employee
    ):
        """存在しないスキルIDは 404。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"skill_id": str(uuid.uuid4()), "self_level": 3}
        res = await client.post(
            f"/api/v1/employees/{member_employee.id}/skills",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 404

    async def test_apply_skill_duplicate(
        self, client: AsyncClient, member_employee: Employee, pending_skill: EmployeeSkill
    ):
        """同じスキルの重複申請は 409。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"skill_id": pending_skill.skill_id, "self_level": 4}
        res = await client.post(
            f"/api/v1/employees/{member_employee.id}/skills",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 409

    async def test_apply_skill_invalid_level(
        self, client: AsyncClient, member_employee: Employee, skill: Skill
    ):
        """self_level が 1〜5 以外は 422。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"skill_id": skill.id, "self_level": 6}
        res = await client.post(
            f"/api/v1/employees/{member_employee.id}/skills",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 422


# ── スキル一覧取得 ────────────────────────────────────────────────────────────

class TestListEmployeeSkills:
    async def test_list_own_skills(
        self, client: AsyncClient, member_employee: Employee, pending_skill: EmployeeSkill
    ):
        """本人は自分のスキルを取得できる。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        res = await client.get(
            f"/api/v1/employees/{member_employee.id}/skills",
            headers=headers,
        )
        assert res.status_code == 200
        assert len(res.json()) == 1

    async def test_member_cannot_list_others_skills(
        self, client: AsyncClient, member_employee: Employee, admin_employee: Employee
    ):
        """memberは他人のスキルを閲覧できない（403）。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        res = await client.get(
            f"/api/v1/employees/{admin_employee.id}/skills",
            headers=headers,
        )
        assert res.status_code == 403

    async def test_manager_can_list_others_skills(
        self,
        client: AsyncClient,
        manager_employee: Employee,
        manager_headers: dict,
        member_employee: Employee,
        pending_skill: EmployeeSkill,
    ):
        """managerは他人のスキルを閲覧できる。"""
        res = await client.get(
            f"/api/v1/employees/{member_employee.id}/skills",
            headers=manager_headers,
        )
        assert res.status_code == 200
        assert len(res.json()) == 1

    async def test_filter_by_status(
        self, client: AsyncClient, auth_headers: dict, member_employee: Employee, pending_skill: EmployeeSkill
    ):
        """status フィルターが機能する。"""
        res = await client.get(
            f"/api/v1/employees/{member_employee.id}/skills?status=APPROVED",
            headers=auth_headers,
        )
        assert res.status_code == 200
        assert len(res.json()) == 0


# ── スキル承認・差し戻し ──────────────────────────────────────────────────────

class TestApproveRejectSkill:
    async def test_approve_skill(
        self,
        client: AsyncClient,
        manager_headers: dict,
        pending_skill: EmployeeSkill,
    ):
        """managerがスキルを承認できる。"""
        res = await client.patch(
            f"/api/v1/employee-skills/{pending_skill.id}/approve",
            json={"approved_level": 3, "approver_comment": "問題なし"},
            headers=manager_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "APPROVED"
        assert data["approved_level"] == 3

    async def test_reject_skill(
        self,
        client: AsyncClient,
        manager_headers: dict,
        pending_skill: EmployeeSkill,
    ):
        """managerがスキルを差し戻せる。"""
        res = await client.patch(
            f"/api/v1/employee-skills/{pending_skill.id}/reject",
            json={"approver_comment": "証拠が不足しています"},
            headers=manager_headers,
        )
        assert res.status_code == 200
        assert res.json()["status"] == "REJECTED"

    async def test_member_cannot_approve(
        self,
        client: AsyncClient,
        member_employee: Employee,
        pending_skill: EmployeeSkill,
    ):
        """memberは承認できない（403）。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        res = await client.patch(
            f"/api/v1/employee-skills/{pending_skill.id}/approve",
            json={"approved_level": 3},
            headers=headers,
        )
        assert res.status_code == 403

    async def test_approve_not_found(
        self, client: AsyncClient, manager_headers: dict
    ):
        """存在しない申請の承認は 404。"""
        res = await client.patch(
            f"/api/v1/employee-skills/{uuid.uuid4()}/approve",
            json={"approved_level": 2},
            headers=manager_headers,
        )
        assert res.status_code == 404

    async def test_double_approve_conflict(
        self,
        client: AsyncClient,
        manager_headers: dict,
        pending_skill: EmployeeSkill,
    ):
        """承認済みスキルを再承認すると 409。"""
        await client.patch(
            f"/api/v1/employee-skills/{pending_skill.id}/approve",
            json={"approved_level": 3},
            headers=manager_headers,
        )
        res = await client.patch(
            f"/api/v1/employee-skills/{pending_skill.id}/approve",
            json={"approved_level": 3},
            headers=manager_headers,
        )
        assert res.status_code == 409


# ── 資格マスタ一覧 ────────────────────────────────────────────────────────────

class TestListCertMasters:
    async def test_list_cert_masters(
        self, client: AsyncClient, auth_headers: dict, cert_master: CertificationMaster
    ):
        """資格マスタ一覧を取得できる。"""
        res = await client.get("/api/v1/certification-masters", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "AWS Certified SAA"

    async def test_list_cert_masters_requires_auth(self, client: AsyncClient):
        """未認証アクセスは 403。"""
        res = await client.get("/api/v1/certification-masters")
        assert res.status_code == 403


# ── 資格申請 ──────────────────────────────────────────────────────────────────

class TestApplyCertification:
    async def test_apply_cert_with_master(
        self, client: AsyncClient, member_employee: Employee, cert_master: CertificationMaster
    ):
        """資格マスタIDを使った申請ができる。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "certification_master_id": cert_master.id,
            "obtained_at": "2025-06-01",
            "score": "800",
        }
        res = await client.post(
            f"/api/v1/employees/{member_employee.id}/certifications",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "PENDING"
        assert data["certification_master"]["name"] == "AWS Certified SAA"

    async def test_apply_cert_custom_name(
        self, client: AsyncClient, member_employee: Employee
    ):
        """custom_name を使ったカスタム資格申請ができる。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "custom_name": "社内技術認定試験",
            "obtained_at": "2025-03-01",
        }
        res = await client.post(
            f"/api/v1/employees/{member_employee.id}/certifications",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 201
        assert res.json()["custom_name"] == "社内技術認定試験"

    async def test_apply_cert_no_name_fails(
        self, client: AsyncClient, member_employee: Employee
    ):
        """certification_master_id も custom_name もない場合は 422。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"obtained_at": "2025-03-01"}
        res = await client.post(
            f"/api/v1/employees/{member_employee.id}/certifications",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 422

    async def test_apply_cert_forbidden_for_other(
        self, client: AsyncClient, member_employee: Employee, admin_employee: Employee, cert_master: CertificationMaster
    ):
        """他人の資格申請は 403。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"certification_master_id": cert_master.id, "obtained_at": "2025-01-01"}
        res = await client.post(
            f"/api/v1/employees/{admin_employee.id}/certifications",
            json=payload,
            headers=headers,
        )
        assert res.status_code == 403


# ── 資格承認・差し戻し ────────────────────────────────────────────────────────

class TestApproveRejectCert:
    async def test_approve_cert(
        self,
        client: AsyncClient,
        manager_headers: dict,
        pending_cert: EmployeeCertification,
    ):
        """managerが資格を承認できる。"""
        res = await client.patch(
            f"/api/v1/certifications/{pending_cert.id}/approve",
            json={"approver_comment": "証明書確認済み"},
            headers=manager_headers,
        )
        assert res.status_code == 200
        assert res.json()["status"] == "APPROVED"

    async def test_reject_cert(
        self,
        client: AsyncClient,
        manager_headers: dict,
        pending_cert: EmployeeCertification,
    ):
        """managerが資格を差し戻せる。"""
        res = await client.patch(
            f"/api/v1/certifications/{pending_cert.id}/reject",
            json={"approver_comment": "証明書が不鮮明です"},
            headers=manager_headers,
        )
        assert res.status_code == 200
        assert res.json()["status"] == "REJECTED"

    async def test_double_approve_cert_conflict(
        self,
        client: AsyncClient,
        manager_headers: dict,
        pending_cert: EmployeeCertification,
    ):
        """承認済み資格の再承認は 409。"""
        await client.patch(
            f"/api/v1/certifications/{pending_cert.id}/approve",
            json={},
            headers=manager_headers,
        )
        res = await client.patch(
            f"/api/v1/certifications/{pending_cert.id}/approve",
            json={},
            headers=manager_headers,
        )
        assert res.status_code == 409


# ── 承認キュー ────────────────────────────────────────────────────────────────

class TestPendingApprovals:
    async def test_list_pending_approvals(
        self,
        client: AsyncClient,
        manager_headers: dict,
        pending_skill: EmployeeSkill,
        pending_cert: EmployeeCertification,
    ):
        """managerが承認待ち一覧を取得できる。"""
        res = await client.get("/api/v1/approvals/pending", headers=manager_headers)
        assert res.status_code == 200
        data = res.json()
        assert "skills" in data
        assert "certifications" in data
        assert len(data["skills"]) == 1
        assert len(data["certifications"]) == 1
        assert data["skills"][0]["skill_name"] == "Python"
        assert data["certifications"][0]["cert_name"] == "AWS Certified SAA"

    async def test_member_cannot_list_pending(
        self, client: AsyncClient, member_employee: Employee
    ):
        """memberは承認キューを閲覧できない（403）。"""
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}
        res = await client.get("/api/v1/approvals/pending", headers=headers)
        assert res.status_code == 403
