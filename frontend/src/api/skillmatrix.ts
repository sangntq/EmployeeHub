/**
 * スキルマトリクス API クライアント
 *
 * エンジニアごとのスキル保有状況をマトリクス形式で取得する。
 */
import apiClient from './client'
import type { EmployeeListItem } from './employees'

export interface SkillInfo {
  id: string
  name: string
}

export interface SkillMatrixCategory {
  id: string
  name_ja: string
  skills: SkillInfo[]
}

export interface EngineerSkillEntry {
  skill_id: string
  level: number | null
  years: number | null
}

export interface EngineerRow {
  employee: EmployeeListItem
  skills: Record<string, EngineerSkillEntry>
}

export interface SkillMatrixResponse {
  categories: SkillMatrixCategory[]
  engineers: EngineerRow[]
}

export interface SkillMatrixParams {
  location?: string
  level_min?: number
  category_id?: string
  free_only?: boolean
  search?: string
}

export const skillMatrixApi = {
  get: (params?: SkillMatrixParams) =>
    apiClient.get<SkillMatrixResponse>('/skills/matrix', { params }).then(r => r.data),
}
