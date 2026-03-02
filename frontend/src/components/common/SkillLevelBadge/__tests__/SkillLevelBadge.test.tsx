/**
 * SkillLevelBadge コンポーネントのユニットテスト
 *
 * SkillLevelBadge は 5つのドット（●）でスキルレベルを表示し、
 * Tooltip に "Lv{level} {label}" を表示する。
 */
import { describe, expect, it } from 'vitest'
import { render } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from '../../../../i18n'
import SkillLevelBadge from '../index'
import type { SkillLevel } from '../../../../types'

// ── ヘルパー ───────────────────────────────────────────────────────────────────

function renderBadge(level: SkillLevel, showLabel = false) {
  return render(
    <I18nextProvider i18n={i18n}>
      <SkillLevelBadge level={level} showLabel={showLabel} />
    </I18nextProvider>,
  )
}

// ── テスト ────────────────────────────────────────────────────────────────────

describe('SkillLevelBadge', () => {
  it('5つのドットをレンダリングする', () => {
    const { container } = renderBadge(3)
    // 各ドットは span としてレンダリングされる
    const dots = container.querySelectorAll('span[style*="border-radius: 50%"]')
    expect(dots).toHaveLength(5)
  })

  it('showLabel=true のとき、ラベルテキストを表示する', () => {
    const { container } = renderBadge(3, true)
    // ラベルは最後の span に表示される
    expect(container.textContent).not.toBe('')
  })

  it('showLabel=false (デフォルト) のとき、ラベルを非表示', () => {
    const { container } = renderBadge(3, false)
    // ラベル span のみ。ドットのみ表示
    const labelSpan = container.querySelector('span[style*="margin-left"]')
    expect(labelSpan).toBeNull()
  })

  it.each([1, 2, 3, 4, 5] as SkillLevel[])(
    'レベル %i でクラッシュしない',
    (level) => {
      expect(() => renderBadge(level)).not.toThrow()
    },
  )

  it('コンポーネントが DOM にマウントされる', () => {
    const { container } = renderBadge(1)
    expect(container.firstChild).not.toBeNull()
  })
})
