/**
 * 入退社トレンドチャート — recharts GroupedBarChart
 * 各月に入社（紫）・退社（赤）の2本バーを表示する。
 */
import { useTranslation } from 'react-i18next'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { HeadcountTrendItem } from '../../api/dashboard'

interface Props {
  data: HeadcountTrendItem[]
}

export default function HeadcountTrendChart({ data }: Props) {
  const { t } = useTranslation()

  // X軸ラベル: "2026-03" → "03月" (現地化は不要; 年月番号で十分)
  const formatted = data.map(d => ({
    ...d,
    label: d.month.slice(5),  // "03" のみ表示
  }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={formatted} margin={{ top: 4, right: 12, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
        <Tooltip
          formatter={(value: number | undefined, name: string | undefined) => {
            const label = name === 'joined'
              ? t('dashboard.headcountJoined')
              : t('dashboard.headcountLeft')
            return [`${value ?? 0}`, label]
          }}
          labelFormatter={(label: unknown) => `${label}月`}
        />
        <Legend
          formatter={(value: unknown) =>
            (value as string) === 'joined'
              ? t('dashboard.headcountJoined')
              : t('dashboard.headcountLeft')
          }
        />
        <Bar dataKey="joined" fill="#722ed1" radius={[3, 3, 0, 0]} />
        <Bar dataKey="left" fill="#f5222d" radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
