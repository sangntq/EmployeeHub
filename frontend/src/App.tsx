import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import AppLayout from './components/common/AppLayout'
import LoginPage from './pages/Login'
import DashboardPage from './pages/Dashboard'
import EmployeeListPage from './pages/Employees/List'
import EmployeeDetailPage from './pages/Employees/Detail'
import ApprovalQueuePage from './pages/Approvals'
import SearchPage from './pages/Search'
import AlertsPage from './pages/Alerts'
import SkillSheetPage from './pages/SkillSheet'
import NotificationsPage from './pages/Notifications'
import NotFoundPage from './pages/NotFound'

/** 未認証の場合 /login にリダイレクトするラッパー */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 公開ルート */}
        <Route path="/login" element={<LoginPage />} />

        {/* 認証が必要なルート */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />

          {/* Phase 1 */}
          <Route path="employees" element={<EmployeeListPage />} />
          <Route path="employees/:id" element={<EmployeeDetailPage />} />

          {/* Phase 2 */}
          <Route path="approvals" element={<ApprovalQueuePage />} />

          {/* Phase 4 */}
          <Route path="search" element={<SearchPage />} />

          {/* Phase 6 */}
          <Route path="alerts" element={<AlertsPage />} />

          {/* Phase 7 */}
          <Route path="skillsheet" element={<SkillSheetPage />} />

          {/* Phase 8 */}
          <Route path="notifications" element={<NotificationsPage />} />
          {/* <Route path="reports" element={<ReportsPage />} /> */}
          {/* <Route path="settings" element={<SettingsPage />} /> */}

          <Route path="*" element={<NotFoundPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}
