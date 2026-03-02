import { Tag } from 'antd'
import { CheckCircleOutlined, ClockCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import type { ApprovalStatus } from '../../../types'

const CONFIG: Record<ApprovalStatus, { color: string; icon: React.ReactNode }> = {
  PENDING:  { color: 'gold',    icon: <ClockCircleOutlined /> },
  APPROVED: { color: 'green',   icon: <CheckCircleOutlined /> },
  REJECTED: { color: 'red',     icon: <CloseCircleOutlined /> },
}

interface Props {
  status: ApprovalStatus
}

export default function ApprovalBadge({ status }: Props) {
  const { t } = useTranslation()
  const { color, icon } = CONFIG[status]
  return (
    <Tag color={color} icon={icon}>
      {t(`approval.${status}`)}
    </Tag>
  )
}
