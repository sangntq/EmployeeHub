"""スキルマトリクスサービス"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.models.skill import EmployeeSkill, Skill, SkillCategory
from app.models.work_status import WorkStatus
from app.schemas.employee import EmployeeListItem
from app.schemas.skillmatrix import (
    SkillInfo,
    EngineerSkillEntry,
    SkillMatrixCategory,
    EngineerRow,
    SkillMatrixResponse,
)


async def get_skill_matrix(
    db: AsyncSession,
    location: str | None = None,
    level_min: int | None = None,
    category_id: str | None = None,
    free_only: bool = False,
    search: str | None = None,
) -> SkillMatrixResponse:
    """スキルマトリクスを返す。

    Args:
        db: DBセッション
        location: office_location フィルター
        level_min: 承認済みスキルレベルの下限（以上の社員のみ）
        category_id: スキルカテゴリ ID フィルター
        free_only: True の場合、FREE_IMMEDIATE または FREE_PLANNED の社員のみ
        search: 社員名・番号の部分一致検索
    """
    # ── アクティブ社員を取得 ────────────────────────────────────────────────
    emp_query = (
        select(Employee)
        .where(Employee.is_active == True)
        .options(selectinload(Employee.department))
        .order_by(Employee.employee_number)
    )
    if location:
        emp_query = emp_query.where(Employee.office_location == location)
    if search:
        like_pattern = f"%{search}%"
        emp_query = emp_query.where(
            or_(
                Employee.name_ja.ilike(like_pattern),
                Employee.name_en.ilike(like_pattern),
                Employee.employee_number.ilike(like_pattern),
            )
        )
    if free_only:
        # WorkStatus サブクエリで FREE_IMMEDIATE / FREE_PLANNED の社員 ID に絞る
        free_subq = (
            select(WorkStatus.employee_id)
            .where(WorkStatus.status.in_(["FREE_IMMEDIATE", "FREE_PLANNED"]))
            .scalar_subquery()
        )
        emp_query = emp_query.where(Employee.id.in_(free_subq))

    emp_result = await db.execute(emp_query)
    employees = list(emp_result.scalars().all())

    if not employees:
        return SkillMatrixResponse(categories=[], engineers=[])

    employee_ids = [e.id for e in employees]

    # ── 全スキルマスタを取得（カテゴリ含む） ──────────────────────────────────
    all_skills_query = (
        select(Skill, SkillCategory)
        .join(SkillCategory, Skill.category_id == SkillCategory.id)
        .where(Skill.is_active == True)
    )
    if category_id:
        all_skills_query = all_skills_query.where(Skill.category_id == category_id)

    all_skills_result = await db.execute(all_skills_query)
    all_skills_rows = all_skills_result.all()

    # カテゴリ・スキルのマスタマップを構築
    cat_map: dict[str, SkillCategory] = {}
    skill_map: dict[str, Skill] = {}
    for (skill, category) in all_skills_rows:
        cat_map[category.id] = category
        skill_map[skill.id] = skill

    # ── APPROVED スキルを一括取得 ───────────────────────────────────────────
    skill_query = (
        select(EmployeeSkill)
        .where(
            EmployeeSkill.employee_id.in_(employee_ids),
            EmployeeSkill.status == "APPROVED",
        )
    )
    if category_id:
        skill_query = skill_query.where(
            EmployeeSkill.skill_id.in_(list(skill_map.keys()))
        )

    skill_result = await db.execute(skill_query)
    emp_skill_rows = skill_result.scalars().all()

    # ── データ集計 ──────────────────────────────────────────────────────────
    # emp_id -> {skill_id: EngineerSkillEntry}
    emp_skill_map: dict[str, dict[str, EngineerSkillEntry]] = {eid: {} for eid in employee_ids}

    for emp_skill in emp_skill_rows:
        if emp_skill.skill_id not in skill_map:
            continue
        emp_skill_map[emp_skill.employee_id][emp_skill.skill_id] = EngineerSkillEntry(
            skill_id=emp_skill.skill_id,
            level=emp_skill.approved_level,
            years=float(emp_skill.experience_years) if emp_skill.experience_years is not None else None,
        )

    # level_min フィルター：少なくとも 1 スキルで approved_level >= level_min の社員のみ
    if level_min is not None:
        filtered_employees = []
        for emp in employees:
            entries = emp_skill_map.get(emp.id, {})
            if any(
                entry.level is not None and entry.level >= level_min
                for entry in entries.values()
            ):
                filtered_employees.append(emp)
        employees = filtered_employees

    # ── カテゴリ・スキル構造を構築（全マスタを含む） ────────────────────────
    # sort_order 昇順でカテゴリをソート
    sorted_cats = sorted(cat_map.values(), key=lambda c: (c.sort_order, c.name_ja))

    categories: list[SkillMatrixCategory] = []
    for cat in sorted_cats:
        # このカテゴリの全スキル一覧（スキル名アルファベット順）
        cat_skills = sorted(
            [s for s in skill_map.values() if s.category_id == cat.id],
            key=lambda s: (s.name_ja or s.name).lower(),
        )
        skill_infos = [
            SkillInfo(id=s.id, name=s.name_ja if s.name_ja else s.name)
            for s in cat_skills
        ]
        categories.append(
            SkillMatrixCategory(id=cat.id, name_ja=cat.name_ja, skills=skill_infos)
        )

    # ── エンジニア行を構築 ─────────────────────────────────────────────────
    engineers: list[EngineerRow] = []
    for emp in employees:
        emp_item = EmployeeListItem.model_validate(emp)
        engineers.append(
            EngineerRow(
                employee=emp_item,
                skills=emp_skill_map.get(emp.id, {}),
            )
        )

    return SkillMatrixResponse(categories=categories, engineers=engineers)
