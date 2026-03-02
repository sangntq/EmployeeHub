import apiClient from './client'

export interface ProjectInfo {
  id: string
  name: string
  client_name: string | null
  industry: string | null
}

export interface EmployeeProjectItem {
  id: string
  employee_id: string
  project_id: string
  project: ProjectInfo
  role: string
  started_at: string
  ended_at: string | null
  tech_stack: string[] | null
  team_size: number | null
  responsibilities: string | null
  achievements: string | null
  sort_order: number
  created_at: string
  updated_at: string
}

export interface EmployeeProjectCreateData {
  project_name: string
  client_name?: string | null
  industry?: string | null
  role: string
  started_at: string
  ended_at?: string | null
  tech_stack?: string[] | null
  team_size?: number | null
  responsibilities?: string | null
  achievements?: string | null
}

export interface EmployeeProjectUpdateData {
  project_name?: string
  client_name?: string | null
  industry?: string | null
  role?: string
  started_at?: string
  ended_at?: string | null
  tech_stack?: string[] | null
  team_size?: number | null
  responsibilities?: string | null
  achievements?: string | null
}

export interface VisaInfo {
  id: string
  employee_id: string
  visa_type: string | null
  residence_card_number: string | null
  expires_at: string | null
  notes: string | null
  updated_at: string
}

export interface VisaUpdateData {
  visa_type?: string | null
  residence_card_number?: string | null
  expires_at?: string | null
  notes?: string | null
}

export const projectsApi = {
  listProjects: (employeeId: string) =>
    apiClient.get<EmployeeProjectItem[]>(`/employees/${employeeId}/projects`).then(r => r.data),

  addProject: (employeeId: string, data: EmployeeProjectCreateData) =>
    apiClient.post<EmployeeProjectItem>(`/employees/${employeeId}/projects`, data).then(r => r.data),

  updateProject: (projectId: string, data: EmployeeProjectUpdateData) =>
    apiClient.put<EmployeeProjectItem>(`/employee-projects/${projectId}`, data).then(r => r.data),

  deleteProject: (projectId: string) =>
    apiClient.delete(`/employee-projects/${projectId}`),

  reorderProjects: (employeeId: string, orderedIds: string[]) =>
    apiClient.patch<EmployeeProjectItem[]>(`/employees/${employeeId}/projects/reorder`, { ordered_ids: orderedIds }).then(r => r.data),

  getVisa: (employeeId: string) =>
    apiClient.get<VisaInfo | null>(`/employees/${employeeId}/visa`).then(r => r.data),

  updateVisa: (employeeId: string, data: VisaUpdateData) =>
    apiClient.put<VisaInfo>(`/employees/${employeeId}/visa`, data).then(r => r.data),
}
