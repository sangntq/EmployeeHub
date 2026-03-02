/**
 * 拠点別人員分布ドーナツチャート — recharts PieChart
 */
import { useTranslation } from 'react-i18next'
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { DistributionItem } from '../../api/dashboard'

interface Props {
  data: DistributionItem[]
}

const COLORS = ['#1677ff', '#52c41a', '#faad14', '#f5222d', '#722ed1']

export default function LocationDonutChart({ data }: Props) {
  const { t } = useTranslation()

  if (data.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '32px 0', color: '#8c8c8c', fontSize: 13 }}>
        {t('common.noData')}
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={data}
          dataKey="count"
          nameKey="label"
          innerRadius={50}
          outerRadius={80}
          paddingAngle={3}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number | undefined, name: string | undefined) => [
            `${value ?? 0}`,
            t(`officeLocation.${name ?? ''}`),
          ]}
        />
        <Legend
          formatter={(label: unknown) => t(`officeLocation.${label as string}`)}
          iconSize={10}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
