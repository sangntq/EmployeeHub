import apiClient from './client'

export interface SkillCriteria {
  skill_id: string
  level_min?: number
  experience_years_min?: number
  required: boolean
}

export interface SearchFilter {
  skills?: SkillCriteria[]
  work_statuses?: string[]
  office_locations?: string[]
  work_style?: string
  japanese_level?: string
  free_from_before?: string
  certification_ids?: string[]
  page?: number
  per_page?: number
}

export interface DepartmentEmbed {
  id: string
  name_ja: string
}

export interface WorkStatusEmbed {
  status: string
  free_from: string | null
}

export interface EmployeeEmbed {
  id: string
  employee_number: string
  name_ja: string
  name_en: string | null
  department: DepartmentEmbed | null
  office_location: string
  work_style: string
  japanese_level: string | null
  avatar_url: string | null
}

export interface SearchResultItem {
  employee: EmployeeEmbed
  work_status: WorkStatusEmbed | null
  match_score: number
  matched_skills: string[]
  missing_skills: string[]
}

export interface SearchResponse {
  items: SearchResultItem[]
  total: number
  page: number
  per_page: number
}

export interface SavedSearchCreate {
  name: string
  criteria: Record<string, unknown>
}

export interface SavedSearchResponse {
  id: string
  name: string
  criteria: Record<string, unknown>
  created_at: string
}

// ── AI自然言語検索 ─────────────────────────────────────────────────────────────

export interface AIParseRequest {
  text: string
}

export interface AISkillMatch {
  skill_id: string
  name: string
  level_min?: number
  required: boolean
}

export interface AIParseResponse {
  summary: string
  criteria: SearchFilter
  skill_matches: AISkillMatch[]
  unmatched_terms: string[]
}

// ── API クライアント ────────────────────────────────────────────────────────────

export const searchApi = {
  filter: (data: SearchFilter) =>
    apiClient.post<SearchResponse>('/search/filter', data).then(r => r.data),

  listSaved: () =>
    apiClient.get<SavedSearchResponse[]>('/search/saved').then(r => r.data),

  saveCriteria: (data: SavedSearchCreate) =>
    apiClient.post<SavedSearchResponse>('/search/saved', data).then(r => r.data),

  deleteSaved: (id: string) =>
    apiClient.delete(`/search/saved/${id}`),

  aiParse: (text: string) =>
    apiClient.post<AIParseResponse>('/search/ai-parse', { text }).then(r => r.data),
}
