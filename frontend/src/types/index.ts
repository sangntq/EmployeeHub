// ============================================================
// 共通型定義
// ============================================================

export type SystemRole = 'member' | 'manager' | 'department_head' | 'sales' | 'director' | 'admin'
export type WorkStatus = 'ASSIGNED' | 'FREE_IMMEDIATE' | 'FREE_PLANNED' | 'INTERNAL' | 'LEAVE' | 'LEAVING'
export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED'
export type EmploymentType = 'FULLTIME' | 'CONTRACT' | 'FREELANCE'
export type WorkStyle = 'ONSITE' | 'REMOTE' | 'HYBRID'
export type OfficeLocation = 'HANOI' | 'HCMC' | 'TOKYO' | 'OSAKA' | 'OTHER'
export type ProjectRole = 'PL' | 'PM' | 'SE' | 'PG' | 'QA' | 'INFRA' | 'DESIGNER' | 'OTHER'
export type SkillLevel = 1 | 2 | 3 | 4 | 5
export type NotificationType =
  | 'VISA_EXPIRY'
  | 'CERT_EXPIRY'
  | 'SKILL_APPROVED'
  | 'SKILL_REJECTED'
  | 'CERT_APPROVED'
  | 'CERT_REJECTED'
  | 'ASSIGNMENT_ENDING'
  | 'APPROVAL_REQUESTED'

// ============================================================
// 認証
// ============================================================

export interface AuthUser {
  id: string
  email: string
  name: string
  employeeId: string
  systemRole: SystemRole
  avatarUrl?: string
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
  expiresIn: number
}

// ============================================================
// 部署
// ============================================================

export interface Department {
  id: string
  nameJa: string
  nameEn?: string
  nameVi?: string
  parentId?: string
}

// ============================================================
// 社員
// ============================================================

export interface Employee {
  id: string
  employeeNumber: string
  nameJa: string
  nameEn?: string
  nameVi?: string
  department?: Department
  systemRole: SystemRole
  officeLocation: OfficeLocation
  employmentType: EmploymentType
  workStyle: WorkStyle
  joinedAt: string
  email: string
  phone?: string
  slackId?: string
  avatarUrl?: string
  isActive: boolean
  workStatus?: WorkStatusRecord
  topSkills?: string[]
}

export interface WorkStatusRecord {
  status: WorkStatus
  freeFrom?: string
  note?: string
  updatedAt: string
}

// ============================================================
// スキル
// ============================================================

export interface SkillCategory {
  id: string
  nameJa: string
  nameEn: string
  skills: Skill[]
}

export interface Skill {
  id: string
  name: string
  nameJa?: string
  categoryId: string
}

export interface EmployeeSkill {
  id: string
  skill: Skill
  selfLevel: SkillLevel
  approvedLevel?: SkillLevel
  experienceYears?: number
  lastUsedAt?: string
  status: ApprovalStatus
  evidenceFileUrl?: string
  selfComment?: string
  approverComment?: string
  approvedAt?: string
  createdAt: string
}

// ============================================================
// 資格
// ============================================================

export interface CertificationMaster {
  id: string
  name: string
  category: string
  issuer?: string
  hasExpiry: boolean
}

export interface EmployeeCertification {
  id: string
  certificationMaster?: CertificationMaster
  customName?: string
  score?: string
  obtainedAt: string
  expiresAt?: string
  fileUrl?: string
  status: ApprovalStatus
  approverComment?: string
  approvedAt?: string
  createdAt: string
}

// ============================================================
// プロジェクト経歴
// ============================================================

export interface EmployeeProject {
  id: string
  projectName: string
  clientName?: string
  industry?: string
  role: ProjectRole
  startedAt: string
  endedAt?: string
  techStack: string[]
  teamSize?: number
  responsibilities?: string
  achievements?: string
  sortOrder: number
}

// ============================================================
// ビザ
// ============================================================

export interface VisaInfo {
  visaType?: string
  residenceCardNumber?: string
  expiresAt?: string
  notes?: string
  updatedAt: string
}

// ============================================================
// 通知
// ============================================================

export interface Notification {
  id: string
  type: NotificationType
  title: string
  body?: string
  isRead: boolean
  relatedEntityType?: string
  relatedEntityId?: string
  createdAt: string
}

// ============================================================
// 検索
// ============================================================

export interface SkillCriteria {
  skillId: string
  name?: string
  levelMin?: SkillLevel
  experienceYearsMin?: number
  required: boolean
}

export interface SearchCriteria {
  skills?: SkillCriteria[]
  workStatuses?: WorkStatus[]
  freeFromBefore?: string
  officeLocations?: OfficeLocation[]
  workStyle?: WorkStyle
  japaneseLevel?: string
  certificationIds?: string[]
  page?: number
  perPage?: number
}

export interface SearchResult {
  employee: Employee
  matchScore: number
  matchedSkills: string[]
  missingSkills: string[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  perPage: number
}

// ============================================================
// API レスポンス
// ============================================================

export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}
