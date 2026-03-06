import apiClient from './client'

export interface EmployeeListItem {
  id: string
  employee_number: string
  name_ja: string
  name_en: string | null
  name_vi: string | null
  department: { id: string; name_ja: string; name_en: string | null } | null
  system_role: string
  office_location: string
  employment_type: string
  work_style: string
  is_active: boolean
  avatar_url: string | null
  japanese_level: string | null
  workload_percent: number | null
  is_mobilizable: boolean
}

export interface EmployeeDetail extends EmployeeListItem {
  email: string
  phone: string | null
  slack_id: string | null
  joined_at: string
  user_id: string | null
}

export interface PaginatedEmployees {
  items: EmployeeListItem[]
  total: number
  page: number
  per_page: number
}

export interface EmployeeListParams {
  page?: number
  per_page?: number
  keyword?: string
  department_id?: string
  system_role?: string
  office_location?: string
  employment_type?: string
  work_style?: string
  is_active?: boolean
}

export interface EmployeeCreateData {
  employee_number: string
  name_ja: string
  name_en?: string
  name_vi?: string
  email: string
  department_id?: string
  system_role?: string
  office_location: string
  employment_type?: string
  work_style?: string
  joined_at: string
  phone?: string
  slack_id?: string
}

export const employeesApi = {
  list: (params?: EmployeeListParams) =>
    apiClient.get<PaginatedEmployees>('/employees', { params }).then(r => r.data),

  get: (id: string) =>
    apiClient.get<EmployeeDetail>(`/employees/${id}`).then(r => r.data),

  create: (data: EmployeeCreateData) =>
    apiClient.post<EmployeeDetail>('/employees', data).then(r => r.data),

  update: (id: string, data: Partial<EmployeeCreateData> & { is_active?: boolean }) =>
    apiClient.put<EmployeeDetail>(`/employees/${id}`, data).then(r => r.data),

  delete: (id: string) =>
    apiClient.delete(`/employees/${id}`),

  uploadAvatar: (id: string, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient
      .post<{ avatar_url: string }>(`/employees/${id}/avatar`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then(r => r.data)
  },
}
