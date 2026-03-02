import { useAuthStore } from '../stores/authStore'
import type { SystemRole } from '../types'

/**
 * 認証・権限チェック用カスタムフック
 */
export function useAuth() {
  const { user, isAuthenticated, logout } = useAuthStore()

  const hasRole = (...roles: SystemRole[]): boolean => {
    if (!user) return false
    return roles.includes(user.systemRole)
  }

  const isAdmin = () => hasRole('admin')
  const isManager = () => hasRole('manager', 'department_head', 'director', 'admin')
  const canSearch = () => hasRole('sales', 'manager', 'department_head', 'director', 'admin')
  const canApprove = () => hasRole('manager', 'department_head', 'admin')
  const canViewDashboard = () => hasRole('manager', 'department_head', 'director', 'admin')

  return {
    user,
    isAuthenticated,
    logout,
    hasRole,
    isAdmin,
    isManager,
    canSearch,
    canApprove,
    canViewDashboard,
  }
}
