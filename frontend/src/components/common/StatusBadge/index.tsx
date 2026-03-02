import { Tag } from 'antd'
import { useTranslation } from 'react-i18next'
import type { WorkStatus } from '../../../types'

const STATUS_COLOR: Record<WorkStatus, string> = {
  ASSIGNED: 'orange',
  FREE_IMMEDIATE: 'green',
  FREE_PLANNED: 'cyan',
  INTERNAL: 'default',
  LEAVE: 'gold',
  LEAVING: 'red',
}

interface Props {
  status: WorkStatus
  freeFrom?: string   // FREE_PLANNED の場合に日付を表示
}

export default function StatusBadge({ status, freeFrom }: Props) {
  const { t } = useTranslation()
  const label = freeFrom && status === 'FREE_PLANNED'
    ? `${t(`workStatus.${status}`)} ${freeFrom}`
    : t(`workStatus.${status}`)

  return <Tag color={STATUS_COLOR[status]}>{label}</Tag>
}
