/**
 * DashboardPage のユニットテスト
 *
 * manager以上のみアクセス可能。TanStack Query は QueryClientProvider でラップ。
 * dashboardApi は vi.mock でモックし、ローディング中のカードタイトルを検証する。
 */
import { describe, it, expect, vi, beforeAll, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import i18n from '../../../i18n'
import { useAuthStore } from '../../../stores/authStore'
import type { AuthUser } from '../../../types'
import DashboardPage from '../index'

// テスト内で日本語訳を使用するため言語を固定する
beforeAll(() => { i18n.changeLanguage('ja') })

// dashboardApi をモック（クエリが非同期で解決するため、初回レンダリングは loading 状態）
vi.mock('../../../api/dashboard', () => ({
  dashboardApi: {
    getOverview: vi.fn().mockResolvedValue({
      total_employees: 100,
      assigned: 80,
      free_immediate: 10,
      free_planned: 10,
      utilization_rate: 80.0,
      pending_approvals: 3,
      alerts: { visa_expiry_30d: 2, cert_expiry_30d: 1 },
    }),
    getUtilizationTrend: vi.fn().mockResolvedValue({ months: [] }),
    getFreeForecast: vi.fn().mockResolvedValue({ forecast: [] }),
    getSkillsDistribution: vi.fn().mockResolvedValue({ items: [] }),
    getSkillHeatmap: vi.fn().mockResolvedValue({ categories: [], items: [] }),
    getHeadcountTrend: vi.fn().mockResolvedValue({ months: [] }),
    getLocationDistribution: vi.fn().mockResolvedValue({ items: [] }),
    getMobilizable: vi.fn().mockResolvedValue({ total: 0, valid_visa: 0, need_visa: 0 }),
    getAlerts: vi.fn().mockResolvedValue({ items: [] }),
  },
}))

// ── ヘルパー ───────────────────────────────────────────────────────────────────

function makeUser(role: string): AuthUser {
  return {
    id: 'u-1',
    email: 'test@test.local',
    name: 'テストユーザー',
    employeeId: 'emp-1',
    systemRole: role as AuthUser['systemRole'],
    avatarUrl: undefined,
  }
}

function renderDashboard() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <I18nextProvider i18n={i18n}>
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <DashboardPage />
        </MemoryRouter>
      </QueryClientProvider>
    </I18nextProvider>,
  )
}

// ── テスト ────────────────────────────────────────────────────────────────────

beforeEach(() => {
  useAuthStore.setState({ user: null, accessToken: null, isAuthenticated: false })
})

describe('DashboardPage', () => {
  it('member はアクセス拒否メッセージを表示する', () => {
    useAuthStore.setState({ user: makeUser('member'), isAuthenticated: true, accessToken: 't' })
    renderDashboard()
    expect(screen.getByText(/manager以上/)).toBeInTheDocument()
  })

  it('sales はアクセス拒否メッセージを表示する', () => {
    useAuthStore.setState({ user: makeUser('sales'), isAuthenticated: true, accessToken: 't' })
    renderDashboard()
    expect(screen.getByText(/manager以上/)).toBeInTheDocument()
  })

  it('manager+ がダッシュボードを表示する（ローディング中は Skeleton）', () => {
    useAuthStore.setState({ user: makeUser('manager'), isAuthenticated: true, accessToken: 't' })
    renderDashboard()
    // クエリがローディング中 → accessDenied は表示されない
    expect(screen.queryByText(/manager以上/)).toBeNull()
    // Skeleton が表示される
    expect(document.querySelector('.ant-skeleton')).toBeInTheDocument()
  })

  it('稼働率推移カードのタイトルを表示する', () => {
    useAuthStore.setState({ user: makeUser('admin'), isAuthenticated: true, accessToken: 't' })
    renderDashboard()
    expect(screen.getByText(/稼働率推移/)).toBeInTheDocument()
  })

  it('フリー予定推移カードのタイトルを表示する', () => {
    useAuthStore.setState({ user: makeUser('admin'), isAuthenticated: true, accessToken: 't' })
    renderDashboard()
    expect(screen.getByText('フリー予定推移')).toBeInTheDocument()
  })

  it('フリー人材（スキル別）カードのタイトルを表示する', () => {
    useAuthStore.setState({ user: makeUser('director'), isAuthenticated: true, accessToken: 't' })
    renderDashboard()
    expect(screen.getByText('フリー人材（スキル別）')).toBeInTheDocument()
  })

  it('アラートサマリーカードと「アラート一覧へ」ボタンを表示する', () => {
    useAuthStore.setState({ user: makeUser('admin'), isAuthenticated: true, accessToken: 't' })
    renderDashboard()
    expect(screen.getByText('期限アラート（今後30日）')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'アラート一覧へ' })).toBeInTheDocument()
  })
})
