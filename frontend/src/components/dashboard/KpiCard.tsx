/**
 * KPI カードコンポーネント
 *
 * ダッシュボード上部の4枚の統計カード（総社員数・稼働中・フリー・承認待ち）に使用する。
 */
import { Card, Statistic } from 'antd'
import type { ReactNode } from 'react'

interface KpiCardProps {
  title: string
  value: number | string
  suffix?: string
  valueStyle?: { color?: string }
  icon?: ReactNode
  extra?: ReactNode
  onClick?: () => void
}

export default function KpiCard({ title, value, suffix, valueStyle, icon, extra, onClick }: KpiCardProps) {
  return (
    <Card
      size="small"
      hoverable={!!onClick}
      onClick={onClick}
      style={{ height: '100%' }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <Statistic
          title={title}
          value={value}
          suffix={suffix}
          valueStyle={valueStyle}
        />
        {icon && (
          <div style={{ fontSize: 28, opacity: 0.15, marginTop: 4 }}>
            {icon}
          </div>
        )}
      </div>
      {extra && <div style={{ marginTop: 4 }}>{extra}</div>}
    </Card>
  )
}
