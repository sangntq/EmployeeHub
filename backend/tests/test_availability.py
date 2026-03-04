"""
稼働可否スケジュール API テスト

- GET /api/v1/availability
"""
import pytest
import uuid
from datetime import date, datetime, UTC

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.employee import Employee


# ── ローカルフィクスチャ ──────────────────────────────────────────────────────

@pytest.fixture
async def manager_employee(db: AsyncSession) -> Employee:
    emp = Employee(
        id=str(uuid.uuid4()),
        employee_number="AVAIL-MGR",
        name_ja="可用性マネージャー",
        name_en="Availability Manager",
        system_role="manager",
        office_location="HANOI",
        employment_type="FULLTIME",
        work_style="REMOTE",
        joined_at=date(2024, 1, 1),
        email="avail_manager@test.local",
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
async def test_availability_200_for_manager(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
):
    """manager ロールは 200 を返す。"""
    resp = await client.get("/api/v1/availability", headers=manager_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_availability_403_for_member(
    client: AsyncClient,
    member_employee: Employee,
    member_headers: dict,
):
    """member ロールは 403 を返す。"""
    resp = await client.get("/api/v1/availability", headers=member_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_availability_response_structure(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
):
    """レスポンスが months_header と items フィールドを持つ。"""
    resp = await client.get("/api/v1/availability?months=3", headers=manager_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "months_header" in data
    assert "items" in data
    assert isinstance(data["months_header"], list)
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_availability_month_count(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
):
    """months パラメーターに従った月数を返す。"""
    resp = await client.get("/api/v1/availability?months=4", headers=manager_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["months_header"]) == 4


@pytest.mark.asyncio
async def test_availability_empty_when_no_employees(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
    db: AsyncSession,
):
    """存在しない拠点でフィルターすると items が空になる。"""
    resp = await client.get(
        "/api/v1/availability?location=OSAKA", headers=manager_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    # OSAKA 拠点の社員はいない（manager_employee は HANOI）
    # manager_employee 自体は HANOI なので OSAKA フィルターでは 0 件
    assert data["items"] == []
