/**
 * 空きカレンダー API クライアント
 *
 * エンジニアの月別稼働状況を取得する。
 */
import apiClient from './client'
import type { EmployeeListItem } from './employees'

export interface AvailabilityMonth {
  month: string
  status: 'FREE' | 'PARTIAL' | 'BUSY'
  allocation: number
  project_name: string | null
}

export interface EmployeeAvailability {
  employee: EmployeeListItem
  months: AvailabilityMonth[]
}

export interface AvailabilityResponse {
  months_header: string[]
  items: EmployeeAvailability[]
}

export interface AvailabilityParams {
  months?: number
  offset_months?: number
  location?: string
  search?: string
  status?: string
}

export const availabilityApi = {
  get: (params?: AvailabilityParams) =>
    apiClient.get<AvailabilityResponse>('/availability', { params }).then(r => r.data),
}
