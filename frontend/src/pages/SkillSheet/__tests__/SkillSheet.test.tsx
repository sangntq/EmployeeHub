/**
 * SkillSheetPage コンポーネントのユニットテスト
 */
import { beforeAll, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { I18nextProvider } from 'react-i18next'
import i18n from '../../../i18n'
import SkillSheetPage from '../index'

// 日本語を強制
beforeAll(() => {
  i18n.changeLanguage('ja')
})

// employeesApi をモック
vi.mock('../../../api/employees', () => ({
  employeesApi: {
    list: vi.fn().mockResolvedValue({ items: [], total: 0, page: 1, per_page: 200 }),
  },
}))

// skillsheetApi をモック
vi.mock('../../../api/skillsheet', () => ({
  skillsheetApi: {
    export: vi.fn().mockResolvedValue({
      download_url: '/api/v1/skillsheet/download/test-token',
      expires_at: '2026-03-01T10:00:00Z',
      filename: 'skillsheet_test.xlsx',
    }),
  },
}))

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <I18nextProvider i18n={i18n}>
          <SkillSheetPage />
        </I18nextProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('SkillSheetPage', () => {
  it('ページタイトル「スキルシート出力」が表示される', () => {
    renderPage()
    // PageHeader はページ本体 + パンくずリストの両方にタイトルをレンダリングするため getAllByText を使用
    expect(screen.getAllByText('スキルシート出力').length).toBeGreaterThanOrEqual(1)
  })

  it('候補者未選択でダウンロードボタンが disabled になる', () => {
    renderPage()
    const btn = screen.getByRole('button', { name: /ダウンロード/i })
    expect(btn).toBeDisabled()
  })

  it('フォーマット選択のラジオ（xlsx/pdf）が表示される', () => {
    renderPage()
    expect(screen.getByText('Excel (.xlsx)')).toBeInTheDocument()
    expect(screen.getByText('PDF')).toBeInTheDocument()
  })

  it('出力スタイルのラジオ（combined/zip）が表示される', () => {
    renderPage()
    expect(screen.getByText('1ファイルにまとめる（シート別）')).toBeInTheDocument()
    expect(screen.getByText('個別ファイルをZIPで出力')).toBeInTheDocument()
  })

  it('ファイル名プレフィックス入力フィールドが表示される', () => {
    renderPage()
    const input = screen.getByPlaceholderText('skillsheet')
    expect(input).toBeInTheDocument()
  })
})
