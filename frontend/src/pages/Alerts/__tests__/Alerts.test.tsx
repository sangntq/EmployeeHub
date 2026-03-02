/**
 * AlertsPage のユニットテスト
 *
 * ビザ期限・資格期限のアラートを Tabs + Table で表示する。
 * dashboardApi.getAlerts をモックしてデータ込みのレンダリングを検証する。
 */
import { describe, it, expect, vi, beforeAll, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import i18n from '../../../i18n'
import { useAuthStore } from '../../../stores/authStore'
import AlertsPage from '../index'

// テスト内で日本語訳を使用するため言語を固定する
beforeAll(() => { i18n.changeLanguage('ja') })

// dashboardApi をモック
vi.mock('../../../api/dashboard', () => ({
  dashboardApi: {
    getAlerts: vi.fn().mockResolvedValue({
      items: [
        {
          type: 'VISA_EXPIRY',
          employee: { id: 'emp-1', name_ja: '田中太郎', employee_number: 'E001' },
          expires_at: '2026-03-07',
          days_remaining: 6,
        },
        {
          type: 'CERT_EXPIRY',
          employee: { id: 'emp-2', name_ja: '鈴木花子', employee_number: 'E002' },
          expires_at: '2026-03-20',
          days_remaining: 19,
        },
      ],
    }),
  },
}))

// ── ヘルパー ───────────────────────────────────────────────────────────────────

function renderAlerts() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <I18nextProvider i18n={i18n}>
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <AlertsPage />
        </MemoryRouter>
      </QueryClientProvider>
    </I18nextProvider>,
  )
}

// ── テスト ────────────────────────────────────────────────────────────────────

beforeEach(() => {
  useAuthStore.setState({ user: null, accessToken: null, isAuthenticated: false })
})

describe('AlertsPage', () => {
  it('ビザ期限タブを表示する', () => {
    renderAlerts()
    expect(screen.getByText(/ビザ期限/)).toBeInTheDocument()
  })

  it('資格期限タブを表示する', () => {
    renderAlerts()
    expect(screen.getByText(/資格期限/)).toBeInTheDocument()
  })

  it('アラートアイテム（氏名）をテーブルに表示する', async () => {
    renderAlerts()
    await waitFor(() => {
      expect(screen.getByText('田中太郎')).toBeInTheDocument()
    })
  })

  it('days_remaining ≤7 のアイテムに赤タグを表示する', async () => {
    renderAlerts()
    await waitFor(() => {
      // 残6日（≤7）→ red タグ
      const tag = screen.getByText(/残6日/)
      expect(tag.closest('.ant-tag')).toHaveClass('ant-tag-red')
    })
  })

  it('「プロフィールを開く」ボタンを表示する', async () => {
    renderAlerts()
    await waitFor(() => {
      const buttons = screen.getAllByRole('button', { name: 'プロフィールを開く' })
      expect(buttons.length).toBeGreaterThan(0)
    })
  })
})
