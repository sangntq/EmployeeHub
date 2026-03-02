import apiClient from './client'

export interface SkillItem {
  id: string
  name: string
  name_ja: string | null
  is_active: boolean
}

export interface SkillCategory {
  id: string
  name_ja: string
  name_en: string
  sort_order: number
  skills: SkillItem[]
}

export interface SkillMasterList {
  categories: SkillCategory[]
}

export interface EmployeeSkill {
  id: string
  skill: SkillItem
  self_level: number
  approved_level: number | null
  experience_years: number | null
  last_used_at: string | null
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  evidence_file_url: string | null
  self_comment: string | null
  approver_comment: string | null
  approved_at: string | null
  created_at: string
  updated_at: string
}

export interface SkillApplyData {
  skill_id: string
  self_level: number
  experience_years?: number
  last_used_at?: string
  self_comment?: string
}

export interface ApproveSkillData {
  approved_level: number
  approver_comment?: string
}

export interface RejectSkillData {
  approver_comment: string
}

export interface PendingSkillItem {
  id: string
  employee_id: string
  employee_name_ja: string
  employee_number: string
  skill_name: string
  self_level: number
  experience_years: number | null
  evidence_file_url: string | null
  self_comment: string | null
  submitted_at: string
}

export const skillsApi = {
  listMasters: () =>
    apiClient.get<SkillMasterList>('/skills').then(r => r.data),

  listEmployeeSkills: (employeeId: string, status?: string) =>
    apiClient
      .get<EmployeeSkill[]>(`/employees/${employeeId}/skills`, {
        params: status ? { status } : undefined,
      })
      .then(r => r.data),

  apply: (employeeId: string, data: SkillApplyData) =>
    apiClient
      .post<EmployeeSkill>(`/employees/${employeeId}/skills`, data)
      .then(r => r.data),

  approve: (skillRecordId: string, data: ApproveSkillData) =>
    apiClient
      .patch<EmployeeSkill>(`/employee-skills/${skillRecordId}/approve`, data)
      .then(r => r.data),

  reject: (skillRecordId: string, data: RejectSkillData) =>
    apiClient
      .patch<EmployeeSkill>(`/employee-skills/${skillRecordId}/reject`, data)
      .then(r => r.data),
}
