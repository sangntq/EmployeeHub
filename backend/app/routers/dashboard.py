"""
ダッシュボード・アラート API ルーター
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_role
from app.models.employee import Employee
from app.schemas.dashboard import (
    AlertListResponse,
    DashboardOverviewResponse,
    FreeForecastResponse,
    HeadcountTrendResponse,
    LocationDistributionResponse,
    SkillHeatmapResponse,
    SkillsDistributionResponse,
    UtilizationTrendResponse,
)
from app.services import dashboard_service

router = APIRouter()

# ダッシュボードはmanager以上が閲覧可能
DASHBOARD_ROLES = ("manager", "department_head", "director", "admin")


@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*DASHBOARD_ROLES)),
):
    """ダッシュボード概要（KPI + アラート件数）。"""
    return await dashboard_service.get_overview(db)


@router.get("/dashboard/utilization-trend", response_model=UtilizationTrendResponse)
async def get_utilization_trend(
    months: int = Query(default=6, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*DASHBOARD_ROLES)),
):
    """過去 N ヶ月の稼働率推移。"""
    return await dashboard_service.get_utilization_trend(db, months)


@router.get("/dashboard/free-forecast", response_model=FreeForecastResponse)
async def get_free_forecast(
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*DASHBOARD_ROLES)),
):
    """今後3ヶ月のフリー人材予測。"""
    return await dashboard_service.get_free_forecast(db)


@router.get("/dashboard/skills-distribution", response_model=SkillsDistributionResponse)
async def get_skills_distribution(
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*DASHBOARD_ROLES)),
):
    """フリー人材のスキル分布（上位10件）。"""
    return await dashboard_service.get_skills_distribution(db)


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    type: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*DASHBOARD_ROLES)),
):
    """期限アラート一覧（ビザ・資格）。"""
    return await dashboard_service.get_alerts(db, type, days)


@router.get("/dashboard/skill-heatmap", response_model=SkillHeatmapResponse)
async def get_skill_heatmap(
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*DASHBOARD_ROLES)),
):
    """全社スキルヒートマップ（カテゴリ × レベル × 人数）。"""
    return await dashboard_service.get_skill_heatmap(db)


@router.get("/dashboard/headcount-trend", response_model=HeadcountTrendResponse)
async def get_headcount_trend(
    months: int = Query(default=12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*DASHBOARD_ROLES)),
):
    """過去 N ヶ月の入退社人数推移。"""
    return await dashboard_service.get_headcount_trend(db, months)


@router.get("/dashboard/location-distribution", response_model=LocationDistributionResponse)
async def get_location_distribution(
    db: AsyncSession = Depends(get_db),
    _: Employee = Depends(require_role(*DASHBOARD_ROLES)),
):
    """拠点別在籍人数分布。"""
    return await dashboard_service.get_location_distribution(db)
