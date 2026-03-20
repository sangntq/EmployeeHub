"""
資格マトリクス API テスト

- GET /api/v1/certifications/matrix
"""
import pytest
import uuid
from datetime import date, datetime, UTC

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.employee import Employee
from app.models.certification import CertificationMaster, EmployeeCertification


# ── ローカルフィクスチャ ──────────────────────────────────────────────────────

@pytest.fixture
async def manager_employee(db: AsyncSession) -> Employee:
    emp = Employee(
        id=str(uuid.uuid4()),
        employee_number="CMATRIX-MGR",
        name_ja="資格マトリクスマネージャー",
        name_en="Cert Matrix Manager",
        system_role="manager",
        office_location="HANOI",
        employment_type="FULLTIME",
        work_style="REMOTE",
        joined_at=date(2024, 1, 1),
        email="certmatrix_manager@test.local",
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
def member_headers(member_employee: Employee) -> dict:
    token = create_access_token(
        subject=member_employee.id,
        extra={"role": "member"},
    )
    return {"Authorization": f"Bearer {token}"}


# ── テスト ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_certmatrix_200_for_manager(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
):
    """manager ロールは 200 を返す。"""
    resp = await client.get("/api/v1/certifications/matrix", headers=manager_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_certmatrix_403_for_member(
    client: AsyncClient,
    member_employee: Employee,
    member_headers: dict,
):
    """member ロールは 403 を返す。"""
    resp = await client.get("/api/v1/certifications/matrix", headers=member_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_certmatrix_response_structure(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
):
    """レスポンスが categories と engineers フィールドを持つ。"""
    resp = await client.get("/api/v1/certifications/matrix", headers=manager_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "categories" in data
    assert "engineers" in data
    assert isinstance(data["categories"], list)
    assert isinstance(data["engineers"], list)


@pytest.mark.asyncio
async def test_certmatrix_shows_all_masters(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
    db: AsyncSession,
):
    """全資格マスタがカテゴリ内に含まれる（保有者がいなくても表示）。"""
    # 資格マスタを追加（誰にも付与しない）
    master = CertificationMaster(
        id=str(uuid.uuid4()),
        name="テスト資格ABC",
        category="CLOUD",
        issuer="テスト機関",
        has_expiry=False,
        is_active=True,
    )
    db.add(master)
    await db.flush()

    resp = await client.get("/api/v1/certifications/matrix", headers=manager_headers)
    assert resp.status_code == 200
    data = resp.json()

    # CLOUD カテゴリにテスト資格が含まれる
    cloud_cats = [c for c in data["categories"] if c["category"] == "CLOUD"]
    assert len(cloud_cats) == 1
    cert_names = [cert["name"] for cert in cloud_cats[0]["certifications"]]
    assert "テスト資格ABC" in cert_names


@pytest.mark.asyncio
async def test_certmatrix_shows_approved_cert(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
    db: AsyncSession,
):
    """APPROVED 資格が社員の certs に含まれる。"""
    master = CertificationMaster(
        id=str(uuid.uuid4()),
        name="テスト認定XYZ",
        category="PM",
        issuer=None,
        has_expiry=True,
        is_active=True,
    )
    db.add(master)
    await db.flush()

    ec = EmployeeCertification(
        id=str(uuid.uuid4()),
        employee_id=manager_employee.id,
        certification_master_id=master.id,
        obtained_at=date(2024, 6, 1),
        expires_at=date(2027, 6, 1),
        status="APPROVED",
        approver_id=manager_employee.id,
        approved_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(ec)
    await db.flush()

    resp = await client.get("/api/v1/certifications/matrix", headers=manager_headers)
    assert resp.status_code == 200
    data = resp.json()

    # manager_employee の certs に master.id が含まれる
    eng = next(
        (e for e in data["engineers"] if e["employee"]["id"] == manager_employee.id),
        None,
    )
    assert eng is not None
    assert master.id in eng["certs"]
    entry = eng["certs"][master.id]
    assert entry["obtained_at"] == "2024-06-01"
    assert entry["expires_at"] == "2027-06-01"
    assert entry["expiry_status"] == "VALID"
