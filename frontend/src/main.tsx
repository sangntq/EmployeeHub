import { StrictMode, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { ConfigProvider } from 'antd'
import jaJP from 'antd/locale/ja_JP'
import enUS from 'antd/locale/en_US'
import viVN from 'antd/locale/vi_VN'
import { I18nextProvider } from 'react-i18next'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import i18n, { type SupportedLanguage, LANGUAGE_STORAGE_KEY } from './i18n'
import App from './App'

const queryClient = new QueryClient()

// AntD の locale と i18next の言語をマッピング
const antdLocaleMap = { ja: jaJP, en: enUS, vi: viVN }

function Root() {
  const [currentLang, setCurrentLang] = useState<SupportedLanguage>(
    () => (localStorage.getItem(LANGUAGE_STORAGE_KEY) as SupportedLanguage) ?? 'ja',
  )

  // i18next の言語変更イベントを購読して AntD locale を同期する
  i18n.on('languageChanged', (lng: string) => {
    setCurrentLang(lng as SupportedLanguage)
  })

  return (
    <I18nextProvider i18n={i18n}>
      <ConfigProvider
        locale={antdLocaleMap[currentLang] ?? jaJP}
        theme={{
          token: {
            colorPrimary: '#1677ff',
            borderRadius: 6,
            fontFamily:
              '"Noto Sans JP", "Noto Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
          },
        }}
      >
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </ConfigProvider>
    </I18nextProvider>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Root />
  </StrictMode>,
)
