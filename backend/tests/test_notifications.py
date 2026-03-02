"""通知 API テスト"""
import uuid
import pytest
from datetime import date, datetime, UTC
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.employee import Employee
from app.models.notification import Notification
from app.models.skill import SkillCategory, Skill, EmployeeSkill
from app.models.certification import CertificationMaster, EmployeeCertification


# ── ヘルパーフィクスチャ ──────────────────────────────────────────────────────

@pytest.fixture
async def member2_employee(db: AsyncSession) -> Employee:
    """別の一般メンバー社員を作成して返す。"""
    emp = Employee(
        id=str(uuid.uuid4()),
        user_id=None,
        employee_number="TEST-003",
        name_ja="テストメンバー2",
        name_en="Test Member 2",
        system_role="member",
        office_location="TOKYO",
        employment_type="FULLTIME",
        work_style="REMOTE",
        joined_at=date(2024, 1, 1),
        email="member2@test.local",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(emp)
    await db.flush()
    return emp


@pytest.fixture
def member_token(member_employee: Employee) -> str:
    return create_access_token(
        subject=member_employee.id,
        extra={"role": member_employee.system_role},
    )


@pytest.fixture
def member_headers(member_token: str) -> dict:
    return {"Authorization": f"Bearer {member_token}"}


@pytest.fixture
def member2_token(member2_employee: Employee) -> str:
    return create_access_token(
        subject=member2_employee.id,
        extra={"role": member2_employee.system_role},
    )


@pytest.fixture
def member2_headers(member2_token: str) -> dict:
    return {"Authorization": f"Bearer {member2_token}"}


async def _create_notification(
    db: AsyncSession,
    recipient_id: str,
    notif_type: str = "SKILL_APPROVED",
    title: str = "テスト通知",
    is_read: bool = False,
) -> Notification:
    """テスト用通知を直接DBに作成する。"""
    notif = Notification(
        id=str(uuid.uuid4()),
        recipient_id=recipient_id,
        type=notif_type,
        title=title,
        body="テスト本文",
        is_read=is_read,
        created_at=datetime.now(UTC),
    )
    db.add(notif)
    await db.flush()
    return notif


# ── 一覧取得テスト ────────────────────────────────────────────────────────────

class TestListNotifications:
    async def test_list_own_notifications(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, member_headers: dict
    ):
        """自分宛の通知を取得できる。"""
        await _create_notification(db, member_employee.id)
        await _create_notification(db, member_employee.id, title="通知2")
        await db.commit()

        r = await client.get("/api/v1/notifications", headers=member_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["unread_count"] == 2

    async def test_cannot_see_others_notifications(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, member2_employee: Employee,
        member_headers: dict,
    ):
        """他人宛の通知は見えない。"""
        await _create_notification(db, member2_employee.id)
        await db.commit()

        r = await client.get("/api/v1/notifications", headers=member_headers)
        assert r.status_code == 200
        assert r.json()["total"] == 0

    async def test_filter_unread(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, member_headers: dict
    ):
        """is_read=false フィルタが効く。"""
        await _create_notification(db, member_employee.id, is_read=False)
        await _create_notification(db, member_employee.id, is_read=True, title="既読通知")
        await db.commit()

        r = await client.get("/api/v1/notifications?is_read=false", headers=member_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 1
        assert data["unread_count"] == 1

    async def test_unread_count_reflects_read_status(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, member_headers: dict
    ):
        """未読件数が正確に返る。"""
        await _create_notification(db, member_employee.id, is_read=True)
        await _create_notification(db, member_employee.id, is_read=False)
        await db.commit()

        r = await client.get("/api/v1/notifications", headers=member_headers)
        data = r.json()
        assert data["total"] == 2
        assert data["unread_count"] == 1

    async def test_requires_auth(self, client: AsyncClient):
        """認証なしは 401 または 403。"""
        r = await client.get("/api/v1/notifications")
        assert r.status_code in (401, 403)


# ── 既読マークテスト ──────────────────────────────────────────────────────────

class TestMarkAsRead:
    async def test_mark_single_notification_read(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, member_headers: dict
    ):
        """単体既読マークが機能する。"""
        notif = await _create_notification(db, member_employee.id, is_read=False)
        await db.commit()

        r = await client.patch(
            f"/api/v1/notifications/{notif.id}/read",
            headers=member_headers,
        )
        assert r.status_code == 204

        # 未読数が0になっていることを確認
        list_r = await client.get("/api/v1/notifications", headers=member_headers)
        assert list_r.json()["unread_count"] == 0

    async def test_mark_nonexistent_notification_404(
        self, client: AsyncClient,
        member_employee: Employee, member_headers: dict
    ):
        """存在しない通知IDは404。"""
        r = await client.patch(
            f"/api/v1/notifications/{uuid.uuid4()}/read",
            headers=member_headers,
        )
        assert r.status_code == 404

    async def test_cannot_mark_others_notification(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, member2_employee: Employee,
        member_headers: dict
    ):
        """他人の通知は既読にできない（403）。"""
        notif = await _create_notification(db, member2_employee.id)
        await db.commit()

        r = await client.patch(
            f"/api/v1/notifications/{notif.id}/read",
            headers=member_headers,
        )
        assert r.status_code == 403

    async def test_mark_all_notifications_read(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, member_headers: dict
    ):
        """全件既読マークが機能する。"""
        await _create_notification(db, member_employee.id)
        await _create_notification(db, member_employee.id, title="通知2")
        await db.commit()

        r = await client.patch("/api/v1/notifications/read-all", headers=member_headers)
        assert r.status_code == 204

        list_r = await client.get("/api/v1/notifications", headers=member_headers)
        assert list_r.json()["unread_count"] == 0


# ── スキル承認/差し戻し → 通知自動生成テスト ─────────────────────────────────

@pytest.fixture
async def skill_category(db: AsyncSession) -> SkillCategory:
    cat = SkillCategory(
        id=str(uuid.uuid4()),
        name_ja="言語",
        name_en="Language",
        sort_order=1,
    )
    db.add(cat)
    await db.flush()
    return cat


@pytest.fixture
async def skill(db: AsyncSession, skill_category: SkillCategory) -> Skill:
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
async def pending_skill(
    db: AsyncSession, member_employee: Employee, skill: Skill
) -> EmployeeSkill:
    """PENDING 状態のスキル申請を作成して返す。"""
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
    return es


class TestSkillApprovalNotifications:
    async def test_skill_approved_creates_notification(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, pending_skill: EmployeeSkill,
        auth_headers: dict, member_headers: dict,
        admin_employee: Employee,
    ):
        """スキル承認 → 申請者に SKILL_APPROVED 通知が作成される。"""
        await db.commit()

        # 正しいURL: PATCH /employee-skills/{id}/approve
        r = await client.patch(
            f"/api/v1/employee-skills/{pending_skill.id}/approve",
            json={"approved_level": 3},
            headers=auth_headers,
        )
        assert r.status_code == 200

        # 通知を確認
        list_r = await client.get("/api/v1/notifications", headers=member_headers)
        items = list_r.json()["items"]
        approved_notifs = [n for n in items if n["type"] == "SKILL_APPROVED"]
        assert len(approved_notifs) >= 1
        assert "Python" in approved_notifs[0]["title"]

    async def test_skill_rejected_creates_notification(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, pending_skill: EmployeeSkill,
        auth_headers: dict, member_headers: dict,
        admin_employee: Employee,
    ):
        """スキル差し戻し → 申請者に SKILL_REJECTED 通知が作成される。"""
        await db.commit()

        r = await client.patch(
            f"/api/v1/employee-skills/{pending_skill.id}/reject",
            json={"approver_comment": "レベルが不足しています"},
            headers=auth_headers,
        )
        assert r.status_code == 200

        list_r = await client.get("/api/v1/notifications", headers=member_headers)
        items = list_r.json()["items"]
        rejected_notifs = [n for n in items if n["type"] == "SKILL_REJECTED"]
        assert len(rejected_notifs) >= 1
        assert "Python" in rejected_notifs[0]["title"]


# ── 資格承認/差し戻し → 通知自動生成テスト ───────────────────────────────────

@pytest.fixture
async def cert_master(db: AsyncSession) -> CertificationMaster:
    """CertificationMaster には created_at フィールドがない。"""
    cm = CertificationMaster(
        id=str(uuid.uuid4()),
        name="AWS SAA",
        category="CLOUD",
        issuer="Amazon",
        is_active=True,
    )
    db.add(cm)
    await db.flush()
    return cm


@pytest.fixture
async def pending_cert(
    db: AsyncSession, member_employee: Employee, cert_master: CertificationMaster
) -> EmployeeCertification:
    ec = EmployeeCertification(
        id=str(uuid.uuid4()),
        employee_id=member_employee.id,
        certification_master_id=cert_master.id,
        status="PENDING",
        obtained_at=date(2024, 1, 1),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(ec)
    await db.flush()
    return ec


class TestCertApprovalNotifications:
    async def test_cert_approved_creates_notification(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, pending_cert: EmployeeCertification,
        auth_headers: dict, member_headers: dict,
        admin_employee: Employee,
    ):
        """資格承認 → CERT_APPROVED 通知が作成される。"""
        await db.commit()

        # 正しいURL: PATCH /certifications/{id}/approve
        r = await client.patch(
            f"/api/v1/certifications/{pending_cert.id}/approve",
            json={},
            headers=auth_headers,
        )
        assert r.status_code == 200

        list_r = await client.get("/api/v1/notifications", headers=member_headers)
        items = list_r.json()["items"]
        approved_notifs = [n for n in items if n["type"] == "CERT_APPROVED"]
        assert len(approved_notifs) >= 1
        assert "AWS SAA" in approved_notifs[0]["title"]

    async def test_cert_rejected_creates_notification(
        self, client: AsyncClient, db: AsyncSession,
        member_employee: Employee, pending_cert: EmployeeCertification,
        auth_headers: dict, member_headers: dict,
        admin_employee: Employee,
    ):
        """資格差し戻し → CERT_REJECTED 通知が作成される。"""
        await db.commit()

        r = await client.patch(
            f"/api/v1/certifications/{pending_cert.id}/reject",
            json={"approver_comment": "証明書が不鮮明です"},
            headers=auth_headers,
        )
        assert r.status_code == 200

        list_r = await client.get("/api/v1/notifications", headers=member_headers)
        items = list_r.json()["items"]
        rejected_notifs = [n for n in items if n["type"] == "CERT_REJECTED"]
        assert len(rejected_notifs) >= 1
