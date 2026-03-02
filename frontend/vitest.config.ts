import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    // jsdom でブラウザ環境をシミュレート
    environment: 'jsdom',
    // テスト実行前に setupTests を読み込む
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    // カバレッジ設定
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/test/**', 'src/vite-env.d.ts'],
    },
  },
})
