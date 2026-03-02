/**
 * Vitest グローバルセットアップ
 * - @testing-library/jest-dom のカスタムマッチャーを追加
 * - 各テスト後に DOM・モックをリセット
 */
import '@testing-library/jest-dom'
import { afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// Ant Design の useBreakpoint（Grid/Row）が matchMedia を使うため jsdom 向けモック
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// 各テスト後に React コンポーネントをアンマウントして状態を初期化
afterEach(() => {
  cleanup()
})
