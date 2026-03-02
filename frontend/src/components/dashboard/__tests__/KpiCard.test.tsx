/**
 * KpiCard コンポーネントのユニットテスト
 */
import { describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import KpiCard from '../KpiCard'

describe('KpiCard', () => {
  it('タイトル・値・suffix を表示する', () => {
    render(<KpiCard title="総社員数" value={42} suffix="名" />)
    expect(screen.getByText('総社員数')).toBeInTheDocument()
    // Ant Design Statistic は value を span に分割してレンダリングする
    expect(screen.getByText('42')).toBeInTheDocument()
    expect(screen.getByText('名')).toBeInTheDocument()
  })

  it('extra コンテンツを表示する', () => {
    render(<KpiCard title="稼働中" value={30} extra={<span>稼働率: 80%</span>} />)
    expect(screen.getByText('稼働率: 80%')).toBeInTheDocument()
  })

  it('onClick が指定された場合にクリックで呼ばれる', () => {
    const handleClick = vi.fn()
    const { container } = render(
      <KpiCard title="承認待ち" value={5} onClick={handleClick} />,
    )
    fireEvent.click(container.querySelector('.ant-card')!)
    expect(handleClick).toHaveBeenCalledOnce()
  })
})
