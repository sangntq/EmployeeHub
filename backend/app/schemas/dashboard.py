"""
ダッシュボード・アラート用 Pydantic スキーマ
"""
from datetime import date

from pydantic import BaseModel


# ── Overview ────────────────────────────────────────────────────────────────

class AlertCounts(BaseModel):
    visa_expiry_30d: int
    cert_expiry_30d: int


class DashboardOverviewResponse(BaseModel):
    total_employees: int
    assigned: int
    free_immediate: int
    free_planned: int
    utilization_rate: float
    pending_approvals: int
    alerts: AlertCounts


# ── Utilization Trend ────────────────────────────────────────────────────────

class UtilizationMonth(BaseModel):
    month: str          # "2026-03"
    assigned: int
    total: int
    utilization_rate: float


class UtilizationTrendResponse(BaseModel):
    months: list[UtilizationMonth]


# ── Free Forecast ────────────────────────────────────────────────────────────

class FreeForecastMonth(BaseModel):
    month: str          # "2026-04"
    free_count: int


class FreeForecastResponse(BaseModel):
    forecast: list[FreeForecastMonth]


# ── Skills Distribution ──────────────────────────────────────────────────────

class SkillDistributionItem(BaseModel):
    skill_name: str
    free_count: int


class SkillsDistributionResponse(BaseModel):
    items: list[SkillDistributionItem]


# ── Alerts ───────────────────────────────────────────────────────────────────

class AlertEmployeeEmbed(BaseModel):
    id: str
    name_ja: str
    employee_number: str


class AlertItem(BaseModel):
    type: str           # "VISA_EXPIRY" | "CERT_EXPIRY"
    employee: AlertEmployeeEmbed
    expires_at: date
    days_remaining: int


class AlertListResponse(BaseModel):
    items: list[AlertItem]


# ── Skill Heatmap ─────────────────────────────────────────────────────────────

class SkillHeatmapCell(BaseModel):
    category: str   # SkillCategory.name_ja
    level: int      # approved_level 1–5
    count: int      # APPROVED EmployeeSkill の distinct employee_id 数


class SkillHeatmapResponse(BaseModel):
    categories: list[str]           # sort_order 順
    items: list[SkillHeatmapCell]


# ── Headcount Movement Trend ──────────────────────────────────────────────────

class HeadcountTrendItem(BaseModel):
    month: str   # "2026-03"
    joined: int  # その月に入社した人数
    left: int    # その月に退社した人数


class HeadcountTrendResponse(BaseModel):
    months: list[HeadcountTrendItem]


# ── Location Distribution ─────────────────────────────────────────────────────

class DistributionItem(BaseModel):
    label: str   # "HANOI", "HCMC", ...
    count: int


class LocationDistributionResponse(BaseModel):
    items: list[DistributionItem]
