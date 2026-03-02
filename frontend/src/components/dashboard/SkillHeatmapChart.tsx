/**
 * スキルヒートマップ — CSS Grid によるカテゴリ × レベル × 人数表示
 */
import { Tooltip } from 'antd'
import { useTranslation } from 'react-i18next'
import type { SkillHeatmapCell } from '../../api/dashboard'

interface Props {
  categories: string[]
  items: SkillHeatmapCell[]
}

const LEVELS = [1, 2, 3, 4, 5]

export default function SkillHeatmapChart({ categories, items }: Props) {
  const { t } = useTranslation()

  // セルの count を高速検索するためのマップ
  const cellMap = new Map<string, number>()
  let maxCount = 0
  for (const item of items) {
    const key = `${item.category}::${item.level}`
    cellMap.set(key, item.count)
    if (item.count > maxCount) maxCount = item.count
  }

  const getColor = (count: number): string => {
    if (count === 0 || maxCount === 0) return '#f5f5f5'
    const alpha = Math.max(0.1, count / maxCount)
    return `rgba(22, 119, 255, ${alpha.toFixed(2)})`
  }

  const gridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: `minmax(120px, auto) repeat(${LEVELS.length}, 1fr)`,
    gap: 2,
    overflowX: 'auto',
  }

  const headerCellStyle: React.CSSProperties = {
    padding: '4px 8px',
    textAlign: 'center',
    fontSize: 12,
    fontWeight: 600,
    color: '#595959',
    background: '#fafafa',
    borderRadius: 4,
    minWidth: 48,
  }

  const labelCellStyle: React.CSSProperties = {
    padding: '6px 8px',
    fontSize: 12,
    color: '#262626',
    display: 'flex',
    alignItems: 'center',
    whiteSpace: 'nowrap',
  }

  const dataCellStyle = (count: number): React.CSSProperties => ({
    background: getColor(count),
    borderRadius: 4,
    minWidth: 48,
    minHeight: 36,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 12,
    fontWeight: count > 0 ? 600 : 400,
    color: count > 0 ? (count / maxCount > 0.6 ? '#fff' : '#1677ff') : '#d9d9d9',
    cursor: count > 0 ? 'default' : undefined,
  })

  if (categories.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '32px 0', color: '#8c8c8c', fontSize: 13 }}>
        {t('common.noData')}
      </div>
    )
  }

  return (
    <div style={gridStyle}>
      {/* ヘッダー行 */}
      <div style={headerCellStyle} />
      {LEVELS.map(lv => (
        <div key={lv} style={headerCellStyle}>
          {t('dashboard.heatmapLevel')} {lv}
        </div>
      ))}

      {/* データ行 */}
      {categories.map(cat => (
        <>
          <div key={`label-${cat}`} style={labelCellStyle}>
            {cat}
          </div>
          {LEVELS.map(lv => {
            const count = cellMap.get(`${cat}::${lv}`) ?? 0
            return (
              <Tooltip
                key={`${cat}-${lv}`}
                title={count > 0 ? t('dashboard.heatmapTooltip', { count }) : undefined}
              >
                <div style={dataCellStyle(count)}>
                  {count > 0 ? count : ''}
                </div>
              </Tooltip>
            )
          })}
        </>
      ))}
    </div>
  )
}
