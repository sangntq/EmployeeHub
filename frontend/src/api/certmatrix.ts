/**
 * 資格マトリクス API クライアント
 */
import apiClient from './client'
import type { EmployeeListItem } from './employees'

export interface CertInfo {
  id: string
  name: string
}

export interface CertMatrixCategory {
  category: string  // LANGUAGE | CLOUD | PM | NETWORK | SECURITY | OTHER
  certifications: CertInfo[]
}

export interface EngineerCertEntry {
  cert_id: string
  obtained_at: string | null
  expires_at: string | null
  expiry_status: string | null  // SOON | VALID | NO_EXPIRY
}

export interface CertEngineerRow {
  employee: EmployeeListItem
  certs: Record<string, EngineerCertEntry>  // cert_master_id -> entry
}

export interface CertMatrixResponse {
  categories: CertMatrixCategory[]
  engineers: CertEngineerRow[]
}

export interface CertMatrixParams {
  location?: string
  category?: string
  free_only?: boolean
  search?: string
}

export const certMatrixApi = {
  get: (params?: CertMatrixParams) =>
    apiClient.get<CertMatrixResponse>('/certifications/matrix', { params }).then(r => r.data),
}
