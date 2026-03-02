import { Tooltip } from 'antd'
import { useTranslation } from 'react-i18next'
import type { SkillLevel } from '../../../types'

interface Props {
  level: SkillLevel
  showLabel?: boolean
}

const DOT_COLOR = ['#d9d9d9', '#91caff', '#4096ff', '#1677ff', '#0958d9']

export default function SkillLevelBadge({ level, showLabel = false }: Props) {
  const { t } = useTranslation()
  const label = t(`skillLevel.level${level}`)

  const dots = (
    <span style={{ display: 'inline-flex', gap: 3, alignItems: 'center' }}>
      {([1, 2, 3, 4, 5] as SkillLevel[]).map((i) => (
        <span
          key={i}
          style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            backgroundColor: i <= level ? DOT_COLOR[level - 1] : '#f0f0f0',
            border: '1px solid #d9d9d9',
            display: 'inline-block',
          }}
        />
      ))}
      {showLabel && (
        <span style={{ marginLeft: 6, fontSize: 12, color: '#595959' }}>{label}</span>
      )}
    </span>
  )

  return (
    <Tooltip title={`Lv${level} ${label}`}>
      {dots}
    </Tooltip>
  )
}
