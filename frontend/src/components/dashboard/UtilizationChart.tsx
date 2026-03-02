/**
 * 稼働率推移チャート（折れ線グラフ）
 *
 * recharts LineChart を使って過去 N ヶ月の稼働率推移を表示する。
 */
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts'
import type { UtilizationMonth } from '../../api/dashboard'

interface UtilizationChartProps {
  data: UtilizationMonth[]
}

export default function UtilizationChart({ data }: UtilizationChartProps) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="month"
          tick={{ fontSize: 11 }}
          tickLine={false}
        />
        <YAxis
          domain={[0, 100]}
          tickFormatter={v => `${v}%`}
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          width={40}
        />
        <Tooltip
          formatter={(value: number | undefined) => [`${value ?? 0}%`, '稼働率']}
          labelStyle={{ fontSize: 12 }}
        />
        <ReferenceLine y={80} stroke="#faad14" strokeDasharray="4 4" />
        <Line
          type="monotone"
          dataKey="utilization_rate"
          stroke="#1677ff"
          strokeWidth={2}
          dot={{ r: 3 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
