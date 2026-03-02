/**
 * StatusBadge コンポーネントのユニットテスト
 *
 * 注意: Ant Design の <Tag> は <span class="ant-tag"> をレンダリングする。
 * <div> と <span> の両方が role="generic" を持つため、getByRole('generic') は
 * 複数要素ヒットしてしまう → container.querySelector('.ant-tag') を使う。
 */
import { describe, expect, it } from 'vitest'
import { render } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from '../../../../i18n'
import StatusBadge from '../index'
import type { WorkStatus } from '../../../../types'

// ── ヘルパー ───────────────────────────────────────────────────────────────────

function renderBadge(status: WorkStatus, freeFrom?: string) {
  return render(
    <I18nextProvider i18n={i18n}>
      <StatusBadge status={status} freeFrom={freeFrom} />
    </I18nextProvider>,
  )
}

// ── テスト ────────────────────────────────────────────────────────────────────

describe('StatusBadge', () => {
  it('ASSIGNED ステータスを表示する', () => {
    const { container } = renderBadge('ASSIGNED')
    // Ant Design Tag は .ant-tag クラスの span としてレンダリングされる
    expect(container.querySelector('.ant-tag')).toBeInTheDocument()
  })

  it('FREE_PLANNED に freeFrom 日付が付与された場合に日付を含む', () => {
    const { container } = renderBadge('FREE_PLANNED', '2025-04-01')
    const tag = container.querySelector('.ant-tag')
    expect(tag?.textContent).toContain('2025-04-01')
  })

  it('FREE_PLANNED でも freeFrom が未指定なら日付なし', () => {
    const { container } = renderBadge('FREE_PLANNED')
    const tag = container.querySelector('.ant-tag')
    expect(tag?.textContent).not.toContain('undefined')
  })

  it.each([
    'ASSIGNED',
    'FREE_IMMEDIATE',
    'FREE_PLANNED',
    'INTERNAL',
    'LEAVE',
    'LEAVING',
  ] as WorkStatus[])('%s ステータスでクラッシュしない', (status) => {
    expect(() => renderBadge(status)).not.toThrow()
  })
})
