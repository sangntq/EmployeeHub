/**
 * ApprovalBadge コンポーネントのユニットテスト
 *
 * 注意: Ant Design の <Tag> は <span class="ant-tag"> をレンダリングする。
 * getByRole('generic') は複数要素にヒットするため、
 * container.querySelector('.ant-tag') を使う。
 *
 * 注意: テスト環境 (jsdom) では navigator.language が 'en' になるため、
 * 文言の検証は i18n.t() を使って言語非依存にする。
 */
import { describe, expect, it } from 'vitest'
import { render } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from '../../../../i18n'
import ApprovalBadge from '../index'
import type { ApprovalStatus } from '../../../../types'

// ── ヘルパー ───────────────────────────────────────────────────────────────────

function renderBadge(status: ApprovalStatus) {
  return render(
    <I18nextProvider i18n={i18n}>
      <ApprovalBadge status={status} />
    </I18nextProvider>,
  )
}

// ── テスト ────────────────────────────────────────────────────────────────────

describe('ApprovalBadge', () => {
  it('PENDING ステータスを表示する', () => {
    const { container } = renderBadge('PENDING')
    const tag = container.querySelector('.ant-tag')
    expect(tag).toBeInTheDocument()
    // i18n.t() で期待値を取得（テスト環境の言語に依存しない）
    expect(tag?.textContent).toContain(i18n.t('approval.PENDING'))
  })

  it('APPROVED ステータスを表示する', () => {
    const { container } = renderBadge('APPROVED')
    const tag = container.querySelector('.ant-tag')
    expect(tag?.textContent).toContain(i18n.t('approval.APPROVED'))
  })

  it('REJECTED ステータスを表示する', () => {
    const { container } = renderBadge('REJECTED')
    const tag = container.querySelector('.ant-tag')
    expect(tag?.textContent).toContain(i18n.t('approval.REJECTED'))
  })

  it.each(['PENDING', 'APPROVED', 'REJECTED'] as ApprovalStatus[])(
    '%s ステータスでクラッシュしない',
    (status) => {
      expect(() => renderBadge(status)).not.toThrow()
    },
  )

  it('PENDING は gold カラーを使う', () => {
    const { container } = renderBadge('PENDING')
    const tag = container.querySelector('.ant-tag-gold')
    expect(tag).toBeInTheDocument()
  })

  it('APPROVED は green カラーを使う', () => {
    const { container } = renderBadge('APPROVED')
    const tag = container.querySelector('.ant-tag-green')
    expect(tag).toBeInTheDocument()
  })

  it('REJECTED は red カラーを使う', () => {
    const { container } = renderBadge('REJECTED')
    const tag = container.querySelector('.ant-tag-red')
    expect(tag).toBeInTheDocument()
  })
})
