"""
検索サービス

フィルター条件でエンジニアを検索し、マッチ度スコアを算出する。
"""
import uuid
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.models.skill import Skill, EmployeeSkill
from app.models.work_status import WorkStatus
from app.models.certification import EmployeeCertification
from app.models.search_log import SearchLog
from app.schemas.search import (
    SearchFilter, SearchResultItem, SearchResponse,
    EmployeeEmbed, WorkStatusEmbed,
    SavedSearchCreate, SavedSearchResponse,
)

# 日本語レベルの順序（低い順）
JAPANESE_LEVEL_ORDER = ["NONE", "N5", "N4", "N3", "N2", "N1", "NATIVE"]


def _japanese_level_index(level: str | None) -> int:
    if level is None:
        return 0
    try:
        return JAPANESE_LEVEL_ORDER.index(level)
    except ValueError:
        return 0


async def search_employees(
    db: AsyncSession,
    criteria: SearchFilter,
    searcher_id: str,
) -> SearchResponse:
    """フィルター条件で社員を検索し、マッチ度スコア付きで返す。"""

    # ── 1. ベースクエリ（active社員 + 部署 + 稼働状況をJOIN）────────────
    query = (
        select(Employee)
        .options(
            selectinload(Employee.department),
            selectinload(Employee.work_status),
            selectinload(Employee.skills).selectinload(EmployeeSkill.skill),
            selectinload(Employee.certifications),
        )
        .where(Employee.is_active == True)
    )
    work_status_joined = False  # work_statuses の二重JOINを防ぐフラグ

    # ── 2. 稼働状況フィルタ ────────────────────────────────────────────
    if criteria.work_statuses:
        query = query.join(WorkStatus, WorkStatus.employee_id == Employee.id, isouter=True)
        work_status_joined = True
        query = query.where(WorkStatus.status.in_(criteria.work_statuses))

    # ── 3. 拠点フィルタ ───────────────────────────────────────────────
    if criteria.office_locations:
        query = query.where(Employee.office_location.in_(criteria.office_locations))

    # ── 4. 勤務スタイルフィルタ ───────────────────────────────────────
    if criteria.work_style:
        query = query.where(Employee.work_style == criteria.work_style)

    # ── 5. 日本語レベルフィルタ ───────────────────────────────────────
    if criteria.japanese_level:
        min_idx = _japanese_level_index(criteria.japanese_level)
        eligible_levels = JAPANESE_LEVEL_ORDER[min_idx:]
        query = query.where(Employee.japanese_level.in_(eligible_levels))

    # ── 6. フリー予定日フィルタ ───────────────────────────────────────
    if criteria.free_from_before:
        if not work_status_joined:
            query = query.join(WorkStatus, WorkStatus.employee_id == Employee.id, isouter=True)
            work_status_joined = True
        query = query.where(
            (WorkStatus.status.in_(["FREE_IMMEDIATE", "FREE_PLANNED"]))
            & (
                (WorkStatus.free_from == None)
                | (WorkStatus.free_from <= criteria.free_from_before)
            )
        )

    # ── 7. 必須スキルフィルタ（サブクエリ）───────────────────────────
    required_skills = [s for s in criteria.skills if s.required]
    for sc in required_skills:
        sub = (
            select(EmployeeSkill.employee_id)
            .where(
                EmployeeSkill.skill_id == sc.skill_id,
                EmployeeSkill.status == "APPROVED",
                EmployeeSkill.approved_level >= (sc.level_min or 1),
            )
        )
        query = query.where(Employee.id.in_(sub))

    # ── 8. 資格フィルタ ───────────────────────────────────────────────
    for cert_id in criteria.certification_ids:
        sub = (
            select(EmployeeCertification.employee_id)
            .where(
                EmployeeCertification.certification_master_id == cert_id,
                EmployeeCertification.status == "APPROVED",
            )
        )
        query = query.where(Employee.id.in_(sub))

    # ── 9. 全件取得してスコア計算 ──────────────────────────────────────
    result = await db.execute(query.order_by(Employee.employee_number))
    all_employees = list(result.scalars().unique().all())

    # スキルマスタ名をまとめて取得（スコア表示用）
    skill_ids = [s.skill_id for s in criteria.skills]
    skill_name_map: dict[str, str] = {}
    if skill_ids:
        sk_result = await db.execute(select(Skill).where(Skill.id.in_(skill_ids)))
        for sk in sk_result.scalars().all():
            skill_name_map[sk.id] = sk.name

    # ── 10. マッチスコア算出 ───────────────────────────────────────────
    scored: list[SearchResultItem] = []
    for emp in all_employees:
        approved_skills = {
            es.skill_id: es.approved_level
            for es in emp.skills
            if es.status == "APPROVED" and es.approved_level is not None
        }

        matched_names: list[str] = []
        missing_names: list[str] = []
        optional_matched = 0

        for sc in criteria.skills:
            skill_name = skill_name_map.get(sc.skill_id, sc.skill_id)
            emp_level = approved_skills.get(sc.skill_id)
            meets_level = emp_level is not None and emp_level >= (sc.level_min or 1)
            if sc.required:
                if meets_level:
                    matched_names.append(skill_name)
                else:
                    missing_names.append(skill_name)
            else:
                if meets_level:
                    optional_matched += 1

        # スコア計算
        if required_skills:
            base_score = int(len(matched_names) / len(required_skills) * 80)
        else:
            base_score = 80

        optional_skills = [s for s in criteria.skills if not s.required]
        bonus = (
            int(optional_matched / len(optional_skills) * 20)
            if optional_skills
            else 20
        )
        match_score = min(100, base_score + bonus)

        ws = emp.work_status
        scored.append(SearchResultItem(
            employee=EmployeeEmbed.model_validate(emp),
            work_status=WorkStatusEmbed.model_validate(ws) if ws else None,
            match_score=match_score,
            matched_skills=matched_names,
            missing_skills=missing_names,
        ))

    # マッチスコアで降順ソート
    scored.sort(key=lambda x: x.match_score, reverse=True)
    total = len(scored)

    # ページネーション
    offset = (criteria.page - 1) * criteria.per_page
    page_items = scored[offset: offset + criteria.per_page]

    # ── 11. 検索ログ保存 ───────────────────────────────────────────────
    log = SearchLog(
        id=str(uuid.uuid4()),
        searcher_id=searcher_id,
        criteria=criteria.model_dump(mode="json"),
        result_count=total,
        created_at=datetime.now(UTC),
    )
    db.add(log)
    await db.commit()

    return SearchResponse(items=page_items, total=total, page=criteria.page, per_page=criteria.per_page)


async def list_saved_searches(db: AsyncSession, searcher_id: str) -> list[SavedSearchResponse]:
    """保存済み検索一覧（本人のみ）。"""
    result = await db.execute(
        select(SearchLog)
        .where(SearchLog.searcher_id == searcher_id, SearchLog.saved_name != None)
        .order_by(SearchLog.created_at.desc())
    )
    logs = list(result.scalars().all())
    return [
        SavedSearchResponse(
            id=log.id,
            name=log.saved_name,
            criteria=log.criteria or {},
            created_at=log.created_at,
        )
        for log in logs
    ]


async def save_search(
    db: AsyncSession,
    body: SavedSearchCreate,
    searcher_id: str,
) -> SavedSearchResponse:
    """検索条件を保存する。"""
    log = SearchLog(
        id=str(uuid.uuid4()),
        searcher_id=searcher_id,
        criteria=body.criteria,
        saved_name=body.name,
        created_at=datetime.now(UTC),
    )
    db.add(log)
    await db.commit()
    return SavedSearchResponse(
        id=log.id,
        name=log.saved_name,
        criteria=log.criteria,
        created_at=log.created_at,
    )


async def delete_saved_search(db: AsyncSession, search_id: str, searcher_id: str) -> None:
    """保存済み検索を削除する（本人のみ）。"""
    from fastapi import HTTPException, status
    result = await db.execute(
        select(SearchLog).where(
            SearchLog.id == search_id,
            SearchLog.searcher_id == searcher_id,
            SearchLog.saved_name != None,
        )
    )
    log = result.scalar_one_or_none()
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="保存済み検索が見つかりません")
    await db.delete(log)
    await db.commit()
