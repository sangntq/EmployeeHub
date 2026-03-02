import apiClient from './client'
import type { PendingSkillItem } from './skills'

export interface CertificationMaster {
  id: string
  name: string
  category: string
  issuer: string | null
  has_expiry: boolean
}

export interface EmployeeCertification {
  id: string
  certification_master: CertificationMaster | null
  custom_name: string | null
  score: string | null
  obtained_at: string
  expires_at: string | null
  file_url: string | null
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  approver_comment: string | null
  approved_at: string | null
  created_at: string
  updated_at: string
}

export interface CertApplyData {
  certification_master_id?: string
  custom_name?: string
  score?: string
  obtained_at: string
  expires_at?: string
  file_url?: string
}

export interface ApproveCertData {
  approver_comment?: string
}

export interface RejectCertData {
  approver_comment: string
}

export interface PendingCertItem {
  id: string
  employee_id: string
  employee_name_ja: string
  employee_number: string
  cert_name: string
  obtained_at: string
  expires_at: string | null
  score: string | null
  file_url: string | null
  submitted_at: string
}

export interface PendingApprovalsResponse {
  skills: PendingSkillItem[]
  certifications: PendingCertItem[]
}

export const certificationsApi = {
  listMasters: () =>
    apiClient.get<CertificationMaster[]>('/certification-masters').then(r => r.data),

  listEmployeeCerts: (employeeId: string, status?: string) =>
    apiClient
      .get<EmployeeCertification[]>(`/employees/${employeeId}/certifications`, {
        params: status ? { status } : undefined,
      })
      .then(r => r.data),

  apply: (employeeId: string, data: CertApplyData) =>
    apiClient
      .post<EmployeeCertification>(`/employees/${employeeId}/certifications`, data)
      .then(r => r.data),

  approve: (certRecordId: string, data: ApproveCertData) =>
    apiClient
      .patch<EmployeeCertification>(`/certifications/${certRecordId}/approve`, data)
      .then(r => r.data),

  reject: (certRecordId: string, data: RejectCertData) =>
    apiClient
      .patch<EmployeeCertification>(`/certifications/${certRecordId}/reject`, data)
      .then(r => r.data),

  listPendingApprovals: () =>
    apiClient.get<PendingApprovalsResponse>('/approvals/pending').then(r => r.data),
}
