"""
社員 API のユニットテスト

テスト対象:
  GET    /api/v1/employees        (一覧)
  GET    /api/v1/employees/{id}   (詳細)
  POST   /api/v1/employees        (作成 - admin のみ)
  PUT    /api/v1/employees/{id}   (更新 - admin のみ)
  DELETE /api/v1/employees/{id}   (無効化 - admin のみ)
"""
import pytest
from httpx import AsyncClient

from app.models.employee import Employee
from app.models.user import User


class TestEmployeeList:
    async def test_list_requires_auth(self, client: AsyncClient):
        """認証なしは 403 を返す。"""
        res = await client.get("/api/v1/employees")
        assert res.status_code == 403

    async def test_list_returns_employees(
        self, client: AsyncClient, admin_employee: Employee, member_employee: Employee, auth_headers: dict
    ):
        """認証済みユーザーは社員一覧を取得できる。"""
        res = await client.get("/api/v1/employees", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 2

    async def test_list_pagination(
        self, client: AsyncClient, admin_employee: Employee, auth_headers: dict
    ):
        """ページネーションパラメータが正常に機能する。"""
        res = await client.get("/api/v1/employees?page=1&per_page=1", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) <= 1
        assert data["page"] == 1
        assert data["per_page"] == 1

    async def test_list_filter_by_role(
        self, client: AsyncClient, admin_employee: Employee, member_employee: Employee, auth_headers: dict
    ):
        """ロールでフィルタリングできる。"""
        res = await client.get("/api/v1/employees?system_role=member", headers=auth_headers)
        assert res.status_code == 200
        items = res.json()["items"]
        for item in items:
            assert item["system_role"] == "member"

    async def test_list_keyword_search(
        self, client: AsyncClient, admin_employee: Employee, auth_headers: dict
    ):
        """キーワード検索が機能する。"""
        res = await client.get("/api/v1/employees?keyword=テスト管理者", headers=auth_headers)
        assert res.status_code == 200
        items = res.json()["items"]
        assert any(item["name_ja"] == "テスト管理者" for item in items)


class TestEmployeeDetail:
    async def test_get_employee(
        self, client: AsyncClient, admin_employee: Employee, auth_headers: dict
    ):
        """既存の社員詳細を取得できる。"""
        res = await client.get(f"/api/v1/employees/{admin_employee.id}", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == admin_employee.id
        assert data["employee_number"] == "TEST-001"

    async def test_get_employee_not_found(self, client: AsyncClient, auth_headers: dict):
        """存在しないIDは 404 を返す。"""
        res = await client.get("/api/v1/employees/nonexistent-id-999", headers=auth_headers)
        assert res.status_code == 404


class TestEmployeeCreate:
    async def test_create_employee_as_admin(
        self, client: AsyncClient, admin_employee: Employee, auth_headers: dict
    ):
        """admin は社員を新規作成できる。"""
        payload = {
            "employee_number": "TEST-NEW",
            "name_ja": "新規テスト社員",
            "name_en": "New Test Employee",
            "email": "new@test.local",
            "office_location": "TOKYO",
            "joined_at": "2025-01-01",
            "system_role": "member",
        }
        res = await client.post("/api/v1/employees", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["employee_number"] == "TEST-NEW"
        assert data["name_ja"] == "新規テスト社員"

    async def test_create_employee_duplicate_number(
        self, client: AsyncClient, admin_employee: Employee, auth_headers: dict
    ):
        """既存の社員番号は 409 を返す。"""
        payload = {
            "employee_number": "TEST-001",  # 重複
            "name_ja": "重複テスト",
            "email": "dup@test.local",
            "office_location": "HANOI",
            "joined_at": "2025-01-01",
        }
        res = await client.post("/api/v1/employees", json=payload, headers=auth_headers)
        assert res.status_code == 409

    async def test_create_employee_non_admin_forbidden(
        self, client: AsyncClient, member_employee: Employee
    ):
        """admin 以外は社員を作成できない（403）。"""
        from app.core.security import create_access_token
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "employee_number": "TEST-FORBIDDEN",
            "name_ja": "禁止テスト",
            "email": "forbidden@test.local",
            "office_location": "HANOI",
            "joined_at": "2025-01-01",
        }
        res = await client.post("/api/v1/employees", json=payload, headers=headers)
        assert res.status_code == 403


class TestEmployeeUpdate:
    async def test_update_employee(
        self, client: AsyncClient, member_employee: Employee, auth_headers: dict
    ):
        """admin は社員情報を更新できる。"""
        res = await client.put(
            f"/api/v1/employees/{member_employee.id}",
            json={"name_en": "Updated Name", "work_style": "HYBRID"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["name_en"] == "Updated Name"
        assert data["work_style"] == "HYBRID"

    async def test_update_nonexistent_employee(self, client: AsyncClient, auth_headers: dict):
        """存在しない社員の更新は 404 を返す。"""
        res = await client.put(
            "/api/v1/employees/nonexistent-id",
            json={"name_en": "Ghost"},
            headers=auth_headers,
        )
        assert res.status_code == 404


class TestEmployeeDelete:
    async def test_delete_employee_as_admin(
        self, client: AsyncClient, member_employee: Employee, auth_headers: dict
    ):
        """admin は社員を無効化（論理削除）できる。"""
        res = await client.delete(
            f"/api/v1/employees/{member_employee.id}",
            headers=auth_headers,
        )
        assert res.status_code == 204

        # 無効化されたことを確認
        res2 = await client.get(
            f"/api/v1/employees/{member_employee.id}",
            headers=auth_headers,
        )
        assert res2.status_code == 200
        assert res2.json()["is_active"] is False
        assert res2.json()["left_at"] is not None

    async def test_delete_employee_non_admin_forbidden(
        self, client: AsyncClient, member_employee: Employee
    ):
        """admin 以外は社員を削除できない（403）。"""
        from app.core.security import create_access_token
        token = create_access_token(subject=member_employee.id, extra={"role": "member"})
        headers = {"Authorization": f"Bearer {token}"}

        res = await client.delete(
            f"/api/v1/employees/{member_employee.id}",
            headers=headers,
        )
        assert res.status_code == 403

    async def test_delete_already_inactive_employee(
        self, client: AsyncClient, member_employee: Employee, auth_headers: dict
    ):
        """すでに無効化された社員を再度削除すると 400 を返す。"""
        # まず無効化
        await client.delete(
            f"/api/v1/employees/{member_employee.id}",
            headers=auth_headers,
        )
        # 再度無効化を試みる
        res = await client.delete(
            f"/api/v1/employees/{member_employee.id}",
            headers=auth_headers,
        )
        assert res.status_code == 400
