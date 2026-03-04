"""
スキルマトリクス API テスト

- GET /api/v1/skills/matrix
"""
import pytest
import uuid
from datetime import date, datetime, UTC

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.employee import Employee
from app.models.skill import Skill, SkillCategory, EmployeeSkill


# ── ローカルフィクスチャ ──────────────────────────────────────────────────────

@pytest.fixture
async def manager_employee(db: AsyncSession) -> Employee:
    emp = Employee(
        id=str(uuid.uuid4()),
        employee_number="MATRIX-MGR",
        name_ja="マトリクスマネージャー",
        name_en="Matrix Manager",
        system_role="manager",
        office_location="HANOI",
        employment_type="FULLTIME",
        work_style="REMOTE",
        joined_at=date(2024, 1, 1),
        email="matrix_manager@test.local",
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
async def test_skillmatrix_200_for_manager(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
):
    """manager ロールは 200 を返す。"""
    resp = await client.get("/api/v1/skills/matrix", headers=manager_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_skillmatrix_403_for_member(
    client: AsyncClient,
    member_employee: Employee,
    member_headers: dict,
):
    """member ロールは 403 を返す。"""
    resp = await client.get("/api/v1/skills/matrix", headers=member_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_skillmatrix_response_has_categories_and_engineers(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
):
    """レスポンスが categories と engineers フィールドを持つ。"""
    resp = await client.get("/api/v1/skills/matrix", headers=manager_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "categories" in data
    assert "engineers" in data
    assert isinstance(data["categories"], list)
    assert isinstance(data["engineers"], list)


@pytest.mark.asyncio
async def test_skillmatrix_empty_when_no_approved_skills(
    client: AsyncClient,
    manager_employee: Employee,
    manager_headers: dict,
    db: AsyncSession,
):
    """承認済みスキルが存在しない場合、categories が空になる。"""
    # スキルカテゴリとスキルを追加するが APPROVED スキルは付与しない
    cat = SkillCategory(
        id=str(uuid.uuid4()),
        name_ja="バックエンド",
        name_en="Backend",
        sort_order=1,
    )
    db.add(cat)
    skill = Skill(
        id=str(uuid.uuid4()),
        category_id=cat.id,
        name="Python",
        name_ja="Python",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db.add(skill)
    await db.flush()

    resp = await client.get("/api/v1/skills/matrix", headers=manager_headers)
    assert resp.status_code == 200
    data = resp.json()
    # APPROVED スキルが誰にも付与されていないので categories は空
    assert data["categories"] == []
