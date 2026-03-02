import { useTranslation } from 'react-i18next'
import { Dropdown, Button } from 'antd'
import { GlobalOutlined } from '@ant-design/icons'
import type { MenuProps } from 'antd'
import { SUPPORTED_LANGUAGES, LANGUAGE_STORAGE_KEY, type SupportedLanguage } from '../../../i18n'

const FLAG: Record<SupportedLanguage, string> = {
  ja: '🇯🇵',
  en: '🇺🇸',
  vi: '🇻🇳',
}

export default function LanguageSwitcher() {
  const { i18n, t } = useTranslation()
  const currentLang = i18n.language as SupportedLanguage

  const items: MenuProps['items'] = SUPPORTED_LANGUAGES.map((lang) => ({
    key: lang,
    label: `${FLAG[lang]}  ${t(`language.${lang}`)}`,
    onClick: () => {
      i18n.changeLanguage(lang)
      localStorage.setItem(LANGUAGE_STORAGE_KEY, lang)
    },
  }))

  return (
    <Dropdown menu={{ items, selectedKeys: [currentLang] }} placement="bottomRight">
      <Button type="text" icon={<GlobalOutlined />}>
        {FLAG[currentLang]}
      </Button>
    </Dropdown>
  )
}
