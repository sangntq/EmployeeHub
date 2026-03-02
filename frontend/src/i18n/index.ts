import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import jaCommon from './locales/ja/common.json'
import enCommon from './locales/en/common.json'
import viCommon from './locales/vi/common.json'

export const SUPPORTED_LANGUAGES = ['ja', 'en', 'vi'] as const
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number]
export const DEFAULT_LANGUAGE: SupportedLanguage = 'ja'
export const LANGUAGE_STORAGE_KEY = 'employeehub-lang'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      ja: { common: jaCommon },
      en: { common: enCommon },
      vi: { common: viCommon },
    },
    fallbackLng: DEFAULT_LANGUAGE,
    defaultNS: 'common',
    // LanguageDetector の設定: localStorage を優先
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: LANGUAGE_STORAGE_KEY,
      caches: ['localStorage'],
    },
    interpolation: {
      escapeValue: false, // React は XSS をデフォルトでエスケープするため不要
    },
  })

export default i18n
