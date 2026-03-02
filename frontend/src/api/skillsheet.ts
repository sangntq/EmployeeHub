import apiClient from './client'

export interface ExportRequest {
  employee_ids: string[]
  format: 'xlsx' | 'pdf'
  output_style: 'combined' | 'zip'
  filename_prefix: string
  include_salary: boolean
}

export interface ExportResponse {
  download_url: string
  expires_at: string
  filename: string
}

export const skillsheetApi = {
  export: (req: ExportRequest) =>
    apiClient.post<ExportResponse>('/skillsheet/export', req).then(r => r.data),
}
