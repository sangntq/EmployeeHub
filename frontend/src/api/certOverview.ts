/**
 * 資格管理概要 API クライアント
 *
 * 資格種別・保有者・期限情報をカテゴリ別にまとめて取得する。
 */
import apiClient from './client'

export interface CertHolder {
  employee_id: string
  name_ja: string
  avatar_url: string | null
  office_location: string
  expires_at: string | null
  expiry_status: 'SOON' | 'VALID' | 'NO_EXPIRY'
}

export interface CertOverviewItem {
  master_id: string | null
  name: string
  issuer: string | null
  category: string
  has_expiry: boolean
  holder_count: number
  expiring_soon: number
  holders: CertHolder[]
}

export interface CertCategoryGroup {
  category: string
  cert_count: number
  total_holders: number
  items: CertOverviewItem[]
}

export interface CertOverviewResponse {
  total_certs: number
  total_holders: number
  expiring_soon_60d: number
  categories: CertCategoryGroup[]
}

export interface CertOverviewParams {
  location?: string
  category?: string
  search?: string
}

export const certOverviewApi = {
  get: (params?: CertOverviewParams) =>
    apiClient.get<CertOverviewResponse>('/certifications/overview', { params }).then(r => r.data),
}
