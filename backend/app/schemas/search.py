"""
検索スキーマ

- SearchFilter: フィルター検索リクエスト
- SearchResultItem: 検索結果1件
- SearchResponse: ページネーション付き検索結果
- SavedSearchCreate: 保存済み検索の作成
- SavedSearchResponse: 保存済み検索のレスポンス
"""
from datetime import date, datetime
from pydantic import BaseModel


class SkillCriteria(BaseModel):
    skill_id: str
    level_min: int | None = None          # 1〜5、未指定は任意レベル
    experience_years_min: float | None = None
    required: bool = True                 # True=必須, False=任意（加点）


class SearchFilter(BaseModel):
    skills: list[SkillCriteria] = []
    work_statuses: list[str] = []         # ASSIGNED / FREE_IMMEDIATE / FREE_PLANNED / ...
    office_locations: list[str] = []      # HANOI / HCMC / TOKYO / OSAKA / OTHER
    work_style: str | None = None         # ONSITE / REMOTE / HYBRID
    japanese_level: str | None = None     # N5 / N4 / N3 / N2 / N1 / NATIVE
    free_from_before: date | None = None  # この日付までにフリーになる
    certification_ids: list[str] = []
    page: int = 1
    per_page: int = 20


class DepartmentEmbed(BaseModel):
    id: str
    name_ja: str

    model_config = {"from_attributes": True}


class WorkStatusEmbed(BaseModel):
    status: str
    free_from: date | None = None

    model_config = {"from_attributes": True}


class EmployeeEmbed(BaseModel):
    id: str
    employee_number: str
    name_ja: str
    name_en: str | None = None
    department: DepartmentEmbed | None = None
    office_location: str
    work_style: str
    japanese_level: str | None = None
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class SearchResultItem(BaseModel):
    employee: EmployeeEmbed
    work_status: WorkStatusEmbed | None
    match_score: int                      # 0〜100
    matched_skills: list[str]             # マッチしたスキル名のリスト
    missing_skills: list[str]             # 不足しているスキル名のリスト


class SearchResponse(BaseModel):
    items: list[SearchResultItem]
    total: int
    page: int
    per_page: int


class SavedSearchCreate(BaseModel):
    name: str
    criteria: dict


class SavedSearchResponse(BaseModel):
    id: str
    name: str
    criteria: dict
    created_at: datetime

    model_config = {"from_attributes": True}


# ── AI自然言語検索スキーマ ─────────────────────────────────────────────────────

class AIParseRequest(BaseModel):
    text: str  # ユーザーの自然言語テキスト（顧客要件・会話内容）


class AISkillMatch(BaseModel):
    """AI解析で抽出されたスキル（名前解決済み）"""
    skill_id: str
    name: str              # スキルマスタの表示名（日本語優先）
    level_min: int | None = None
    required: bool = True


class AIParseResponse(BaseModel):
    """AI解析レスポンス"""
    summary: str                        # Claudeが生成した一行サマリー
    criteria: SearchFilter              # 構造化検索条件（SearchFilter と互換）
    skill_matches: list[AISkillMatch]   # UI表示用スキル情報（名前解決済み）
    unmatched_terms: list[str]          # マスタに存在しなかった用語
