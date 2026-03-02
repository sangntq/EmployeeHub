"""
認証 API のユニットテスト

テスト対象:
  POST /api/v1/auth/login
  POST /api/v1/auth/refresh
  GET  /api/v1/auth/me
  DELETE /api/v1/auth/logout
"""
import pytest
from httpx import AsyncClient

from app.models.employee import Employee
from app.models.user import User


class TestLogin:
    async def test_login_success(self, client: AsyncClient, admin_user: User, admin_employee: Employee):
        """正しいメール＋パスワードでログインできる。"""
        res = await client.post("/api/v1/auth/login", json={
            "email": admin_user.email,
            "password": "TestPass1!",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["employee"]["system_role"] == "admin"
        assert data["employee"]["employee_number"] == "TEST-001"

    async def test_login_wrong_password(self, client: AsyncClient, admin_user: User, admin_employee: Employee):
        """パスワードが間違っている場合は 401 を返す。"""
        res = await client.post("/api/v1/auth/login", json={
            "email": admin_user.email,
            "password": "WrongPassword!",
        })
        assert res.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        """存在しないメールアドレスは 401 を返す。"""
        res = await client.post("/api/v1/auth/login", json={
            "email": "nobody@test.local",
            "password": "SomePass1!",
        })
        assert res.status_code == 401

    async def test_login_inactive_user(self, client: AsyncClient, db, admin_user: User, admin_employee: Employee):
        """無効化されたユーザーはログインできない。"""
        admin_user.is_active = False
        await db.flush()

        res = await client.post("/api/v1/auth/login", json={
            "email": admin_user.email,
            "password": "TestPass1!",
        })
        assert res.status_code == 401


class TestRefresh:
    async def test_refresh_success(self, client: AsyncClient, admin_user: User, admin_employee: Employee):
        """有効なリフレッシュトークンで新しいアクセストークンを取得できる。"""
        login = await client.post("/api/v1/auth/login", json={
            "email": admin_user.email,
            "password": "TestPass1!",
        })
        refresh_token = login.json()["refresh_token"]

        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res.status_code == 200
        assert "access_token" in res.json()

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """無効なトークンは 401 を返す。"""
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.token.here"})
        assert res.status_code == 401


class TestMe:
    async def test_me_success(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        """認証済みユーザーは自分の情報を取得できる。"""
        res = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["system_role"] == "admin"
        assert data["employee_id"] == admin_employee.id

    async def test_me_no_token(self, client: AsyncClient):
        """トークンなしは 403 を返す。"""
        res = await client.get("/api/v1/auth/me")
        assert res.status_code == 403

    async def test_me_invalid_token(self, client: AsyncClient):
        """無効なトークンは 401 を返す。"""
        res = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token"})
        assert res.status_code == 401


class TestLogout:
    async def test_logout_success(self, client: AsyncClient, admin_employee: Employee, auth_headers: dict):
        """認証済みユーザーはログアウトできる（204 が返る）。"""
        res = await client.delete("/api/v1/auth/logout", headers=auth_headers)
        assert res.status_code == 204
