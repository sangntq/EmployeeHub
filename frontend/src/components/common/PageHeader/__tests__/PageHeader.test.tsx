/**
 * PageHeader コンポーネントのユニットテスト
 *
 * PageHeader はタイトル・パンくずリスト・アクションボタンを表示する。
 */
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Button } from 'antd'
import PageHeader from '../index'

// ── テスト ────────────────────────────────────────────────────────────────────

describe('PageHeader', () => {
  it('タイトルを表示する', () => {
    render(<PageHeader title="社員管理" />)
    expect(screen.getByText('社員管理')).toBeInTheDocument()
  })

  it('サブタイトルを表示する', () => {
    render(<PageHeader title="社員管理" subtitle="全社員の管理" />)
    expect(screen.getByText('全社員の管理')).toBeInTheDocument()
  })

  it('breadcrumbs が指定された場合に表示する', () => {
    render(
      <PageHeader
        title="社員詳細"
        breadcrumbs={[
          { title: '社員管理', href: '/employees' },
          { title: '山田太郎' },
        ]}
      />,
    )
    expect(screen.getByText('社員管理')).toBeInTheDocument()
    expect(screen.getByText('山田太郎')).toBeInTheDocument()
  })

  it('breadcrumbs が空の場合に Breadcrumb を表示しない', () => {
    render(<PageHeader title="テスト" breadcrumbs={[]} />)
    // パンくずリストなし → ol.ant-breadcrumb は存在しない
    const breadcrumb = document.querySelector('.ant-breadcrumb')
    expect(breadcrumb).toBeNull()
  })

  it('extra にボタンを指定した場合に表示する', () => {
    render(
      <PageHeader
        title="社員管理"
        extra={<Button>追加</Button>}
      />,
    )
    // Ant Design Button は span 内にテキストを分割する場合があるため getByRole を使う
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('extra が未指定の場合はボタンエリアを表示しない', () => {
    render(<PageHeader title="社員管理" />)
    // extra なし → ボタンなし
    expect(screen.queryByRole('button')).toBeNull()
  })

  it('breadcrumbs のリンク href が正しく設定される', () => {
    render(
      <PageHeader
        title="詳細"
        breadcrumbs={[{ title: 'トップ', href: '/employees' }]}
      />,
    )
    const link = screen.getByRole('link', { name: 'トップ' })
    expect(link).toHaveAttribute('href', '/employees')
  })
})
