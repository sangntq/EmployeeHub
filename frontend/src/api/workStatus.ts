import apiClient from './client'

export interface WorkStatus {
  id: string
  employee_id: string
  status: 'ASSIGNED' | 'FREE_IMMEDIATE' | 'FREE_PLANNED' | 'INTERNAL' | 'LEAVE' | 'LEAVING'
  free_from: string | null
  note: string | null
  updated_at: string
}

export interface WorkStatusUpdateData {
  status: string
  free_from?: string | null
  note?: string | null
}

export interface AssignmentItem {
  id: string
  employee_id: string
  project_id: string
  project_name: string | null
  allocation_percent: number
  started_at: string
  ends_at: string | null
  is_active: boolean
  created_at: string
}

export interface AssignmentCreateData {
  project_id: string
  allocation_percent: number
  started_at: string
  ends_at?: string | null
}

export interface AssignmentUpdateData {
  allocation_percent?: number
  ends_at?: string | null
  is_active?: boolean
}

export const workStatusApi = {
  getWorkStatus: (employeeId: string) =>
    apiClient.get<WorkStatus>(`/employees/${employeeId}/work-status`).then(r => r.data),

  updateWorkStatus: (employeeId: string, data: WorkStatusUpdateData) =>
    apiClient.patch<WorkStatus>(`/employees/${employeeId}/work-status`, data).then(r => r.data),

  listAssignments: (employeeId: string) =>
    apiClient.get<AssignmentItem[]>(`/employees/${employeeId}/assignments`).then(r => r.data),

  createAssignment: (employeeId: string, data: AssignmentCreateData) =>
    apiClient.post<AssignmentItem>(`/employees/${employeeId}/assignments`, data).then(r => r.data),

  updateAssignment: (assignmentId: string, data: AssignmentUpdateData) =>
    apiClient.patch<AssignmentItem>(`/assignments/${assignmentId}`, data).then(r => r.data),
}
