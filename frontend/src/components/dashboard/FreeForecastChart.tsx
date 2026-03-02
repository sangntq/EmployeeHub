/**
 * フリー人材予測チャート（エリアグラフ）
 *
 * recharts AreaChart を使って今後3ヶ月のフリー人材数予測を表示する。
 */
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { FreeForecastMonth } from '../../api/dashboard'

interface FreeForecastChartProps {
  data: FreeForecastMonth[]
}

export default function FreeForecastChart({ data }: FreeForecastChartProps) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="freeGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#52c41a" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#52c41a" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="month"
          tick={{ fontSize: 11 }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          width={36}
          allowDecimals={false}
        />
        <Tooltip
          formatter={(value: number | undefined) => [`${value ?? 0}名`, 'フリー予測']}
          labelStyle={{ fontSize: 12 }}
        />
        <Area
          type="monotone"
          dataKey="free_count"
          stroke="#52c41a"
          strokeWidth={2}
          fill="url(#freeGradient)"
          dot={{ r: 4 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
