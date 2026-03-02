/**
 * ダッシュボード API クライアント
 */
import apiClient from './client'

// ── Overview ────────────────────────────────────────────────────────────────

export interface AlertCounts {
  visa_expiry_30d: number
  cert_expiry_30d: number
}

export interface DashboardOverview {
  total_employees: number
  assigned: number
  free_immediate: number
  free_planned: number
  utilization_rate: number
  pending_approvals: number
  alerts: AlertCounts
}

// ── Utilization Trend ────────────────────────────────────────────────────────

export interface UtilizationMonth {
  month: string          // "2026-03"
  assigned: number
  total: number
  utilization_rate: number
}

export interface UtilizationTrendResponse {
  months: UtilizationMonth[]
}

// ── Free Forecast ────────────────────────────────────────────────────────────

export interface FreeForecastMonth {
  month: string
  free_count: number
}

export interface FreeForecastResponse {
  forecast: FreeForecastMonth[]
}

// ── Skills Distribution ──────────────────────────────────────────────────────

export interface SkillDistributionItem {
  skill_name: string
  free_count: number
}

export interface SkillsDistributionResponse {
  items: SkillDistributionItem[]
}

// ── Alerts ───────────────────────────────────────────────────────────────────

export interface AlertEmployee {
  id: string
  name_ja: string
  employee_number: string
}

export interface AlertItem {
  type: 'VISA_EXPIRY' | 'CERT_EXPIRY'
  employee: AlertEmployee
  expires_at: string
  days_remaining: number
}

export interface AlertListResponse {
  items: AlertItem[]
}

// ── Skill Heatmap ────────────────────────────────────────────────────────────

export interface SkillHeatmapCell {
  category: string
  level: number
  count: number
}

export interface SkillHeatmapResponse {
  categories: string[]
  items: SkillHeatmapCell[]
}

// ── Headcount Trend ───────────────────────────────────────────────────────────

export interface HeadcountTrendItem {
  month: string
  joined: number
  left: number
}

export interface HeadcountTrendResponse {
  months: HeadcountTrendItem[]
}

// ── Location Distribution ─────────────────────────────────────────────────────

export interface DistributionItem {
  label: string
  count: number
}

export interface LocationDistributionResponse {
  items: DistributionItem[]
}

// ── API 関数 ─────────────────────────────────────────────────────────────────

export const dashboardApi = {
  getOverview: () =>
    apiClient.get<DashboardOverview>('/dashboard/overview').then(r => r.data),

  getUtilizationTrend: (months = 6) =>
    apiClient
      .get<UtilizationTrendResponse>(`/dashboard/utilization-trend?months=${months}`)
      .then(r => r.data),

  getFreeForecast: () =>
    apiClient.get<FreeForecastResponse>('/dashboard/free-forecast').then(r => r.data),

  getSkillsDistribution: () =>
    apiClient
      .get<SkillsDistributionResponse>('/dashboard/skills-distribution')
      .then(r => r.data),

  getAlerts: (type?: string, days = 30) =>
    apiClient
      .get<AlertListResponse>(`/alerts?days=${days}${type ? `&type=${type}` : ''}`)
      .then(r => r.data),

  getSkillHeatmap: () =>
    apiClient.get<SkillHeatmapResponse>('/dashboard/skill-heatmap').then(r => r.data),

  getHeadcountTrend: (months = 12) =>
    apiClient
      .get<HeadcountTrendResponse>(`/dashboard/headcount-trend?months=${months}`)
      .then(r => r.data),

  getLocationDistribution: () =>
    apiClient
      .get<LocationDistributionResponse>('/dashboard/location-distribution')
      .then(r => r.data),
}
