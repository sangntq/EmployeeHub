"""
Phase 5: AI自然言語検索 APIテスト（10件）

Anthropic SDK は unittest.mock でモックし、
実際のAPIキー・ネットワークなしでテスト実行可能。
"""
import json
import uuid
import pytest
from datetime import date, datetime, UTC
from unittest.mock import patch, AsyncMock, MagicMock

from app.core.security import create_access_token
from app.models.employee import Employee
from app.models.skill import SkillCategory, Skill
from app.models.search_log import SearchLog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# ── ヘルパー ─────────────────────────────────────────────────────────────────────

def _make_anthropic_response(content_text: str):
    """Anthropic client.messages.create() のモックレスポンスを生成する。"""
    content_block = MagicMock()
    content_block.text = content_text
    msg = MagicMock()
    msg.content = [content_block]
    return msg


def _valid_ai_response(skill_id: str, skill_name: str = "Java") -> str:
    """有効なAI解析レスポンスJSON文字列を返す。"""
    return json.dumps({
        "summary": f"{skill_name}エンジニアを1名募集",
        "skills": [{"skill_id": skill_id, "level_min": 3, "required": True}],
        "japanese_level": "N2",
        "work_style": "REMOTE",
        "office_locations": [],
        "work_statuses": [],
        "free_from_before": None,
        "unmatched_terms": [],
    })


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
def sales_employee_and_headers(db):
    """salesロール社員 + 認証ヘッダーを返すフィクスチャ（asyncで使用）。"""
    pass  # 下記テストで直接作成


# ── テスト ─────────────────────────────────────────────────────────────────────

class TestAIParseDisabled:

    async def test_ai_parse_not_enabled_503(self, client, auth_headers, admin_employee):
        """ANTHROPIC_API_KEY 未設定 → 503。"""
        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = False
            resp = await client.post(
                "/api/v1/search/ai-parse",
                json={"text": "Javaエンジニアが必要"},
                headers=auth_headers,
            )
        assert resp.status_code == 503
        assert "not enabled" in resp.json()["detail"].lower()


class TestAIParseSuccess:

    async def test_ai_parse_success_200(
        self, client, auth_headers, admin_employee, skill_java
    ):
        """正常なAI解析レスポンスが200で返る。"""
        mock_resp = _make_anthropic_response(_valid_ai_response(skill_java.id))

        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = True
            mock_settings.ANTHROPIC_API_KEY = "sk-test"
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_resp)
            with patch("anthropic.AsyncAnthropic", return_value=mock_client):
                resp = await client.post(
                    "/api/v1/search/ai-parse",
                    json={"text": "Javaエンジニア N2以上、リモート希望"},
                    headers=auth_headers,
                )

        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "criteria" in data
        assert "skill_matches" in data
        assert "unmatched_terms" in data

    async def test_ai_parse_skill_id_resolved(
        self, client, auth_headers, admin_employee, skill_java
    ):
        """スキルIDがマスタで正しく解決され、skill_matchesに含まれる。"""
        mock_resp = _make_anthropic_response(_valid_ai_response(skill_java.id))

        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = True
            mock_settings.ANTHROPIC_API_KEY = "sk-test"
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_resp)
            with patch("anthropic.AsyncAnthropic", return_value=mock_client):
                resp = await client.post(
                    "/api/v1/search/ai-parse",
                    json={"text": "Javaエンジニアが必要"},
                    headers=auth_headers,
                )

        data = resp.json()
        assert len(data["skill_matches"]) == 1
        assert data["skill_matches"][0]["skill_id"] == skill_java.id
        assert data["skill_matches"][0]["name"] == "Java"
        assert data["skill_matches"][0]["required"] is True

    async def test_ai_parse_unmatched_terms(
        self, client, auth_headers, admin_employee, skill_java
    ):
        """マスタに存在しないスキル名は unmatched_terms に入る。"""
        ai_json = json.dumps({
            "summary": "Python エンジニア募集",
            "skills": [],
            "japanese_level": None,
            "work_style": None,
            "office_locations": [],
            "work_statuses": [],
            "free_from_before": None,
            "unmatched_terms": ["量子コンピューティング", "ブロックチェーン"],
        })
        mock_resp = _make_anthropic_response(ai_json)

        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = True
            mock_settings.ANTHROPIC_API_KEY = "sk-test"
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_resp)
            with patch("anthropic.AsyncAnthropic", return_value=mock_client):
                resp = await client.post(
                    "/api/v1/search/ai-parse",
                    json={"text": "量子コンピューティングとブロックチェーンの専門家"},
                    headers=auth_headers,
                )

        data = resp.json()
        assert "量子コンピューティング" in data["unmatched_terms"]
        assert "ブロックチェーン" in data["unmatched_terms"]

    async def test_ai_parse_japanese_level_extracted(
        self, client, auth_headers, admin_employee
    ):
        """日本語レベルが criteria.japanese_level として返る。"""
        ai_json = json.dumps({
            "summary": "N1以上の開発者",
            "skills": [],
            "japanese_level": "N1",
            "work_style": None,
            "office_locations": [],
            "work_statuses": [],
            "free_from_before": None,
            "unmatched_terms": [],
        })
        mock_resp = _make_anthropic_response(ai_json)

        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = True
            mock_settings.ANTHROPIC_API_KEY = "sk-test"
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_resp)
            with patch("anthropic.AsyncAnthropic", return_value=mock_client):
                resp = await client.post(
                    "/api/v1/search/ai-parse",
                    json={"text": "日本語N1以上の開発者が必要"},
                    headers=auth_headers,
                )

        data = resp.json()
        assert data["criteria"]["japanese_level"] == "N1"

    async def test_ai_parse_work_style_extracted(
        self, client, auth_headers, admin_employee
    ):
        """勤務スタイルが criteria.work_style として返る。"""
        ai_json = json.dumps({
            "summary": "リモートワーク可能な開発者",
            "skills": [],
            "japanese_level": None,
            "work_style": "REMOTE",
            "office_locations": [],
            "work_statuses": [],
            "free_from_before": None,
            "unmatched_terms": [],
        })
        mock_resp = _make_anthropic_response(ai_json)

        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = True
            mock_settings.ANTHROPIC_API_KEY = "sk-test"
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_resp)
            with patch("anthropic.AsyncAnthropic", return_value=mock_client):
                resp = await client.post(
                    "/api/v1/search/ai-parse",
                    json={"text": "フルリモートで働けるエンジニア"},
                    headers=auth_headers,
                )

        data = resp.json()
        assert data["criteria"]["work_style"] == "REMOTE"


class TestAIParseErrors:

    async def test_ai_parse_invalid_json_422(
        self, client, auth_headers, admin_employee
    ):
        """Claude が無効なJSONを返した場合 → 422。"""
        mock_resp = _make_anthropic_response("これはJSONではありません。テキストのみです。")

        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = True
            mock_settings.ANTHROPIC_API_KEY = "sk-test"
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_resp)
            with patch("anthropic.AsyncAnthropic", return_value=mock_client):
                resp = await client.post(
                    "/api/v1/search/ai-parse",
                    json={"text": "エンジニアが必要"},
                    headers=auth_headers,
                )

        assert resp.status_code == 422


class TestAIParseRBAC:

    async def test_ai_parse_rbac_member_403(
        self, client, member_employee
    ):
        """memberロール → 403。"""
        token = create_access_token(
            subject=member_employee.id,
            extra={"role": member_employee.system_role},
        )
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post(
            "/api/v1/search/ai-parse",
            json={"text": "エンジニアが必要"},
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_ai_parse_rbac_sales_200(
        self, client, db: AsyncSession, skill_java
    ):
        """salesロール → 200（アクセス可能）。"""
        # salesロール社員を作成
        sales_emp = Employee(
            id=str(uuid.uuid4()),
            employee_number="SALES-001",
            name_ja="テスト営業",
            system_role="sales",
            office_location="TOKYO",
            employment_type="FULLTIME",
            work_style="ONSITE",
            joined_at=date(2024, 1, 1),
            email="sales@test.local",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(sales_emp)
        await db.flush()

        token = create_access_token(
            subject=sales_emp.id,
            extra={"role": sales_emp.system_role},
        )
        headers = {"Authorization": f"Bearer {token}"}

        mock_resp = _make_anthropic_response(_valid_ai_response(skill_java.id))

        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = True
            mock_settings.ANTHROPIC_API_KEY = "sk-test"
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_resp)
            with patch("anthropic.AsyncAnthropic", return_value=mock_client):
                resp = await client.post(
                    "/api/v1/search/ai-parse",
                    json={"text": "Javaエンジニアが必要"},
                    headers=headers,
                )

        assert resp.status_code == 200


class TestAIParseLogging:

    async def test_ai_parse_logs_is_ai_search(
        self, client, auth_headers, admin_employee, skill_java, db: AsyncSession
    ):
        """AI解析後、SearchLog(is_ai_search=True) がDBに保存される。"""
        mock_resp = _make_anthropic_response(_valid_ai_response(skill_java.id))
        input_text = "AI検索ログテスト用テキスト"

        with patch("app.services.ai_parser.settings") as mock_settings:
            mock_settings.ai_search_enabled = True
            mock_settings.ANTHROPIC_API_KEY = "sk-test"
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_resp)
            with patch("anthropic.AsyncAnthropic", return_value=mock_client):
                resp = await client.post(
                    "/api/v1/search/ai-parse",
                    json={"text": input_text},
                    headers=auth_headers,
                )

        assert resp.status_code == 200

        # DBにログが保存されているか確認
        result = await db.execute(
            select(SearchLog).where(
                SearchLog.is_ai_search == True,
                SearchLog.raw_input == input_text,
            )
        )
        log = result.scalar_one_or_none()
        assert log is not None
        assert log.is_ai_search is True
        assert log.raw_input == input_text
