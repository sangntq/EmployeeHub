"""
テスト共通フィクスチャ

- SQLite インメモリ DB を使用して PostgreSQL に依存しないテストを実現
- サービス層が commit() を呼ぶため、rollback では分離できない
  → 各テスト後に全テーブルの行を DELETE して独立性を保つ（clean_db autouse）
"""
import pytest
import uuid
from datetime import date, datetime, UTC
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.models.employee import Employee

# ── テスト用 DB（SQLite インメモリ）────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    """セッション開始時にテーブルを作成し、終了時に削除する。"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def clean_db(create_tables):
    """各テスト後に全テーブルの行を DELETE してDB状態をリセットする。

    rollback ではサービス層の commit() を取り消せないため、
    DELETE ALL で確実に分離する。
    """
    yield
    async with test_engine.begin() as conn:
        # 外部キー制約を一時的に無効化してから全テーブル削除
        await conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
        await conn.execute(text("PRAGMA foreign_keys = ON"))


@pytest.fixture
async def db() -> AsyncSession:
    """各テストに独立したDBセッションを提供する。"""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def override_get_db(db: AsyncSession):
    """FastAPI の get_db 依存性をテスト用DBセッションに差し替える。"""
    async def _get_test_db():
        yield db

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client(override_get_db) -> AsyncClient:
    """テスト用の HTTP クライアント。"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── テストデータ作成ヘルパー ────────────────────────────────────────────────────

@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    """管理者ユーザーを DB に作成して返す。"""
    user = User(
        id=str(uuid.uuid4()),
        email="admin@test.local",
        password_hash=hash_password("TestPass1!"),
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(user)
    await db.flush()
    return user


@pytest.fixture
async def admin_employee(db: AsyncSession, admin_user: User) -> Employee:
    """管理者社員を DB に作成して返す。"""
    emp = Employee(
        id=str(uuid.uuid4()),
        user_id=admin_user.id,
        employee_number="TEST-001",
        name_ja="テスト管理者",
        name_en="Test Admin",
        system_role="admin",
        office_location="HANOI",
        employment_type="FULLTIME",
        work_style="REMOTE",
        joined_at=date(2024, 1, 1),
        email=admin_user.email,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(emp)
    await db.flush()
    return emp


@pytest.fixture
async def member_employee(db: AsyncSession) -> Employee:
    """一般メンバー社員（ユーザーなし）を DB に作成して返す。"""
    emp = Employee(
        id=str(uuid.uuid4()),
        user_id=None,
        employee_number="TEST-002",
        name_ja="テストメンバー",
        name_en="Test Member",
        system_role="member",
        office_location="HCMC",
        employment_type="FULLTIME",
        work_style="ONSITE",
        joined_at=date(2024, 6, 1),
        email="member@test.local",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(emp)
    await db.flush()
    return emp


@pytest.fixture
def admin_token(admin_employee: Employee) -> str:
    """管理者用アクセストークンを生成して返す。"""
    return create_access_token(
        subject=admin_employee.id,
        extra={"role": admin_employee.system_role},
    )


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """認証ヘッダー辞書を返す。"""
    return {"Authorization": f"Bearer {admin_token}"}
