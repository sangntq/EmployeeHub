import { Result, Button } from 'antd'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'

export default function NotFoundPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  return (
    <Result
      status="404"
      title="404"
      subTitle={t('page.notFound')}
      extra={
        <Button type="primary" onClick={() => navigate('/')}>
          {t('action.back')}
        </Button>
      }
    />
  )
}
