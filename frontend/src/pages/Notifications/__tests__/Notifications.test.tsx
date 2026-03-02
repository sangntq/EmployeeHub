/**
 * NotificationsPage コンポーネントのユニットテスト
 */
import { beforeAll, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import i18n from '../../../i18n'
import NotificationsPage from '../index'

// 日本語を強制
beforeAll(() => {
  i18n.changeLanguage('ja')
})

// notificationsApi をモック
vi.mock('../../../api/notifications', () => ({
  notificationsApi: {
    getList: vi.fn().mockResolvedValue({
      items: [],
      total: 0,
      unread_count: 0,
      page: 1,
      per_page: 50,
    }),
    markAsRead: vi.fn().mockResolvedValue({}),
    markAllRead: vi.fn().mockResolvedValue({}),
  },
}))

// notificationStore をモック
vi.mock('../../../stores/notificationStore', () => ({
  useNotificationStore: () => ({
    unreadCount: 0,
    fetchUnreadCount: vi.fn(),
  }),
}))

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <I18nextProvider i18n={i18n}>
          <NotificationsPage />
        </I18nextProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('NotificationsPage', () => {
  it('ページタイトル「通知」が表示される', async () => {
    renderPage()
    expect(screen.getByText('通知')).toBeInTheDocument()
  })

  it('ローディング中に Skeleton が表示される', () => {
    const { container } = renderPage()
    // Skeleton は ul.ant-skeleton-paragraph として描画される
    const skeleton = container.querySelector('.ant-skeleton')
    expect(skeleton).toBeInTheDocument()
  })

  it('データ取得後に「全件既読にする」ボタンが表示される', async () => {
    renderPage()
    expect(await screen.findByText('全件既読にする')).toBeInTheDocument()
  })
})
