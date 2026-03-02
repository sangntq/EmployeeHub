"""
AI自然言語検索サービス

顧客要件テキストを Claude API で解析し、構造化された検索条件に変換する。
"""
import json
import uuid
from datetime import datetime, UTC

import anthropic
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.search_log import SearchLog
from app.models.skill import Skill, SkillCategory
from app.schemas.search import (
    AIParseRequest,
    AIParseResponse,
    AISkillMatch,
    SearchFilter,
    SkillCriteria,
)

# 利用するClaude モデル（高速・低コスト）
_MODEL = "claude-haiku-4-5-20251001"

# スキルマスタをSystem promptに含める最大件数
_MAX_SKILLS_IN_PROMPT = 300


async def parse_natural_language(
    text: str,
    db: AsyncSession,
    searcher_id: str,
) -> AIParseResponse:
    """自然言語テキストを解析し、SearchFilter + 解説情報を返す。

    Args:
        text: ユーザーが入力した顧客要件テキスト
        db: 非同期DBセッション
        searcher_id: 検索実行者のEmployee ID（ログ用）

    Returns:
        AIParseResponse

    Raises:
        HTTPException(503): API key未設定 または Anthropic API障害
        HTTPException(422): Claude のレスポンスがJSONとして解析できない場合
    """
    # ── 1. AI機能の有効化チェック ────────────────────────────────────────
    if not settings.ai_search_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI search is not enabled. Set ANTHROPIC_API_KEY in environment.",
        )

    # ── 2. スキルマスタ取得（プロンプトコンテキスト用）──────────────────
    skill_result = await db.execute(
        select(Skill)
        .where(Skill.is_active == True)
        .order_by(Skill.name)
        .limit(_MAX_SKILLS_IN_PROMPT)
    )
    skills = skill_result.scalars().all()

    skill_list_json = json.dumps(
        [{"id": s.id, "name": s.name, "name_ja": s.name_ja or s.name} for s in skills],
        ensure_ascii=False,
    )

    # ── 3. プロンプト構築 ─────────────────────────────────────────────────
    system_prompt = f"""あなたはITエンジニア人材要件をJSONに変換するアシスタントです。

利用可能なスキルマスタ（JSON配列）:
{skill_list_json}

有効なenum値:
- office_locations: HANOI, HCMC, TOKYO, OSAKA, OTHER
- work_styles: ONSITE, REMOTE, HYBRID
- japanese_levels: NONE, N5, N4, N3, N2, N1, NATIVE
- work_statuses: ASSIGNED, FREE_IMMEDIATE, FREE_PLANNED, INTERNAL, LEAVE, LEAVING

以下のJSONスキーマで返答してください（他のテキストは一切含めないこと）:
{{
  "summary": "入力内容の一行サマリー（入力と同じ言語で）",
  "skills": [
    {{"skill_id": "<マスタのid>", "level_min": null, "required": true}}
  ],
  "japanese_level": null,
  "work_style": null,
  "office_locations": [],
  "work_statuses": [],
  "free_from_before": null,
  "unmatched_terms": []
}}

ルール:
- skill_idはスキルマスタのidのみ使用。マスタにないスキル名はunmatched_termsに入れる
- level_min（1〜5）は明示的に言及された場合のみ設定（"3年以上"→level_min:3の目安）
- required: 必須ならtrue、あると良い・歓迎の場合はfalse
- free_from_before: 開始可能時期が述べられていれば "YYYY-MM-DD" 形式
- 明示されていない条件は設定しない（推測しない）
- 日付はISO形式（YYYY-MM-DD）"""

    # ── 4. Claude API 呼び出し ────────────────────────────────────────────
    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model=_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": text}],
        )
        raw_content = message.content[0].text.strip()
    except anthropic.APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unavailable: {e}",
        )

    # ── 5. JSON解析 ───────────────────────────────────────────────────────
    try:
        # コードブロックが含まれる場合は除去
        if raw_content.startswith("```"):
            lines = raw_content.split("\n")
            raw_content = "\n".join(lines[1:-1])
        parsed = json.loads(raw_content)
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not parse AI response as JSON. Please try again.",
        )

    # ── 6. スキルIDの検証・名前解決 ──────────────────────────────────────
    skill_map = {s.id: s for s in skills}
    raw_skills: list[dict] = parsed.get("skills", [])

    skill_matches: list[AISkillMatch] = []
    criteria_skills: list[SkillCriteria] = []
    unmatched_terms: list[str] = list(parsed.get("unmatched_terms", []))

    for item in raw_skills:
        sid = item.get("skill_id", "")
        if sid in skill_map:
            sk = skill_map[sid]
            display_name = sk.name_ja or sk.name
            level_min = item.get("level_min")
            required = item.get("required", True)
            skill_matches.append(
                AISkillMatch(
                    skill_id=sid,
                    name=display_name,
                    level_min=level_min,
                    required=required,
                )
            )
            criteria_skills.append(
                SkillCriteria(
                    skill_id=sid,
                    level_min=level_min,
                    required=required,
                )
            )
        # 無効なIDは無視（Claudeが誤ったIDを返した場合）

    # ── 7. SearchFilter 構築 ──────────────────────────────────────────────
    criteria = SearchFilter(
        skills=criteria_skills,
        japanese_level=parsed.get("japanese_level") or None,
        work_style=parsed.get("work_style") or None,
        office_locations=parsed.get("office_locations", []),
        work_statuses=parsed.get("work_statuses", []),
        free_from_before=parsed.get("free_from_before") or None,
    )

    # ── 8. 検索ログ保存（is_ai_search=True） ─────────────────────────────
    log = SearchLog(
        id=str(uuid.uuid4()),
        searcher_id=searcher_id,
        is_ai_search=True,
        raw_input=text,
        criteria=criteria.model_dump(mode="json"),
        created_at=datetime.now(UTC),
    )
    db.add(log)
    await db.commit()

    return AIParseResponse(
        summary=parsed.get("summary", ""),
        criteria=criteria,
        skill_matches=skill_matches,
        unmatched_terms=unmatched_terms,
    )
