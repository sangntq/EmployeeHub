/**
 * スキルマトリクスページ（グリッド表示）
 *
 * 行＝エンジニア、列＝スキル（カテゴリグループ別ヘッダー）。
 * 各セルは承認レベル（1〜5）を星＋数字で表示する。
 */
import { useState, useCallback, useMemo, useRef } from 'react'
import {
  Input,
  Select,
  Checkbox,
  Row,
  Col,
  Typography,
  Skeleton,
  Tooltip,
} from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import PageHeader from '../../components/common/PageHeader'
import { skillMatrixApi } from '../../api/skillmatrix'
import type { EngineerRow, SkillMatrixCategory } from '../../api/skillmatrix'

import './style.css'

const { Option } = Select

const OFFICE_OPTIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const LEVEL_OPTIONS  = [1, 2, 3, 4, 5]

/** カテゴリヘッダーの色テーマ */
const CATEGORY_THEMES: Record<string, { bg: string; text: string }> = {
  // フロントエンド
  0: { bg: '#2563EB', text: '#fff' },
  // バックエンド
  1: { bg: '#7C3AED', text: '#fff' },
  // DevOps
  2: { bg: '#0D9488', text: '#fff' },
  // DB
  3: { bg: '#6D28D9', text: '#fff' },
  // モバイル
  4: { bg: '#059669', text: '#fff' },
  // AI/ML
  5: { bg: '#DC2626', text: '#fff' },
  // その他
  6: { bg: '#D97706', text: '#fff' },
  7: { bg: '#0891B2', text: '#fff' },
  8: { bg: '#4338CA', text: '#fff' },
  9: { bg: '#BE185D', text: '#fff' },
}

function getCategoryTheme(idx: number) {
  const key = String(idx % 10)
  return CATEGORY_THEMES[key] ?? { bg: '#4B5563', text: '#fff' }
}

/** レベル別セルの色 */
const LEVEL_CELL_COLORS: Record<number, { bg: string; text: string; border: string }> = {
  1: { bg: '#FEF3C7', text: '#78350F', border: '#FDE68A' },
  2: { bg: '#FED7AA', text: '#7C2D12', border: '#FDBA74' },
  3: { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' },
  4: { bg: '#BAE6FD', text: '#0C4A6E', border: '#7DD3FC' },
  5: { bg: '#DDD6FE', text: '#4C1D95', border: '#C4B5FD' },
}

const AVATAR_COLORS = [
  '#4F46E5', '#7C3AED', '#DB2777', '#DC2626',
  '#D97706', '#059669', '#0891B2', '#2563EB',
]

function getAvatarColor(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
}

/** スキルレベルから経験レベルラベルを返す */
function getEngineerLevel(skills: EngineerRow['skills']): string {
  const entries = Object.values(skills).filter(e => e.level != null)
  if (entries.length === 0) return ''
  const avg = entries.reduce((s, e) => s + e.level!, 0) / entries.length
  if (avg >= 4.5) return 'Lead'
  if (avg >= 3.5) return 'Senior'
  if (avg >= 2.5) return 'Middle'
  return 'Junior'
}

/** 名前からイニシャルを生成 */
function getInitials(nameJa: string, nameEn: string | null | undefined): string {
  if (nameEn) {
    const parts = nameEn.split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return nameEn.substring(0, 2).toUpperCase()
  }
  return (nameJa || '?').substring(0, 2)
}

/** 星文字列を生成 */
function renderStars(level: number): string {
  return '★'.repeat(level)
}

/** オフィスからフラグラベルを返す */
function getOfficeFlag(office: string, t: (k: string) => string): { flag: string; label: string; color: string } {
  switch (office) {
    case 'HANOI':
    case 'HCMC':
      return { flag: 'VN', label: t(`officeLocation.${office}`), color: '#DC2626' }
    case 'TOKYO':
    case 'OSAKA':
      return { flag: 'JP', label: t(`officeLocation.${office}`), color: '#2563EB' }
    default:
      return { flag: '🌍', label: t(`officeLocation.${office}`), color: '#6B7280' }
  }
}

export default function SkillMatrixPage() {
  const { t } = useTranslation()
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  const [search, setSearch]         = useState('')
  const [location, setLocation]     = useState<string | undefined>()
  const [levelMin, setLevelMin]     = useState<number | undefined>()
  const [categoryId, setCategoryId] = useState<string | undefined>()
  const [freeOnly, setFreeOnly]     = useState(false)
  const [skillFilter, setSkillFilter] = useState<string[]>([])

  const handleSearchChange = useCallback((e: { target: { value: string } }) => {
    setSearch(e.target.value)
  }, [])

  const params = {
    search:      search      || undefined,
    location:    location    || undefined,
    level_min:   levelMin,
    category_id: categoryId  || undefined,
    free_only:   freeOnly    || undefined,
  }

  const { data, isLoading } = useQuery({
    queryKey: ['skillMatrix', params],
    queryFn:  () => skillMatrixApi.get(params),
    staleTime: 3 * 60 * 1000,
  })

  const categories: SkillMatrixCategory[] = data?.categories ?? []
  const engineers:  EngineerRow[]          = data?.engineers  ?? []

  // スキルフィルター適用後のカテゴリ
  const visibleCategories = useMemo(() => {
    const filterSet = new Set(skillFilter)
    return categories
      .map(cat => {
        if (filterSet.size === 0) return cat
        const filtered = cat.skills.filter(sk => filterSet.has(sk.id))
        return { ...cat, skills: filtered }
      })
      .filter(cat => cat.skills.length > 0)
  }, [categories, skillFilter])

  // 全スキル列のフラットリスト（カテゴリ順）
  const allSkillColumns = useMemo(() => {
    return visibleCategories.flatMap(cat => cat.skills)
  }, [visibleCategories])

  // スキルフィルター用の選択肢（全スキル一覧）
  const allSkillOptions = useMemo(() => {
    return categories.flatMap(cat =>
      cat.skills.map(sk => ({ value: sk.id, label: sk.name, category: cat.name_ja }))
    )
  }, [categories])

  // is_mobilizable フラグ
  const mobilizableSet = useMemo(() => {
    const s = new Set<string>()
    for (const eng of engineers) {
      if (eng.employee.is_mobilizable) s.add(eng.employee.id)
    }
    return s
  }, [engineers])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 104px)' }}>
      <PageHeader title={t('skillMatrix.title')} />

      {/* フィルターバー */}
      <Row gutter={[8, 8]} style={{ marginBottom: 12, flexShrink: 0 }} align="middle">
        <Col flex="220px">
          <Input
            placeholder={t('common.searchPlaceholder')}
            allowClear
            prefix={<SearchOutlined />}
            value={search}
            onChange={handleSearchChange}
          />
        </Col>
        <Col>
          <Select
            placeholder={t('common.officeLocation')}
            allowClear
            style={{ width: 130 }}
            value={location}
            onChange={v => setLocation(v)}
          >
            {OFFICE_OPTIONS.map(o => (
              <Option key={o} value={o}>{t(`officeLocation.${o}`)}</Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Select
            placeholder={t('skillMatrix.levelMin')}
            allowClear
            style={{ width: 120 }}
            value={levelMin}
            onChange={v => setLevelMin(v)}
          >
            {LEVEL_OPTIONS.map(l => (
              <Option key={l} value={l}>Lv {l}+</Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Select
            placeholder={t('skillMatrix.category')}
            allowClear
            style={{ width: 150 }}
            value={categoryId}
            onChange={v => setCategoryId(v)}
          >
            {categories.map(cat => (
              <Option key={cat.id} value={cat.id}>{cat.name_ja}</Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Select
            mode="multiple"
            placeholder={t('skillMatrix.skillFilter')}
            allowClear
            style={{ minWidth: 180, maxWidth: 350 }}
            maxTagCount={2}
            value={skillFilter}
            onChange={v => setSkillFilter(v)}
            options={allSkillOptions}
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
          />
        </Col>
        <Col>
          <Checkbox checked={freeOnly} onChange={e => setFreeOnly(e.target.checked)}>
            <Typography.Text style={{ fontSize: 13 }}>
              {t('skillMatrix.freeOnly')}
            </Typography.Text>
          </Checkbox>
        </Col>
      </Row>

      {/* マトリクステーブル */}
      {isLoading ? (
        <Skeleton active paragraph={{ rows: 12 }} />
      ) : (
        <div
          ref={scrollContainerRef}
          className="skill-matrix-scroll"
          style={{ flex: 1, overflow: 'auto', minHeight: 0 }}
        >
          <table className="skill-matrix-table">
            {/* ── カテゴリグループヘッダー行 ── */}
            <thead>
              <tr className="skill-matrix-cat-row">
                <th
                  className="skill-matrix-engineer-header"
                  rowSpan={2}
                >
                  {t('skillMatrix.engineer')}
                </th>
                {visibleCategories.map((cat, idx) => {
                  const theme = getCategoryTheme(idx)
                  return (
                    <th
                      key={cat.id}
                      colSpan={cat.skills.length}
                      className="skill-matrix-cat-header"
                      style={{
                        backgroundColor: theme.bg,
                        color: theme.text,
                      }}
                    >
                      {cat.name_ja}
                    </th>
                  )
                })}
              </tr>
              {/* ── 個別スキルヘッダー行 ── */}
              <tr className="skill-matrix-skill-row">
                {visibleCategories.map((cat, catIdx) =>
                  cat.skills.map(sk => {
                    const theme = getCategoryTheme(catIdx)
                    return (
                      <th
                        key={sk.id}
                        className="skill-matrix-skill-header"
                        style={{
                          backgroundColor: `${theme.bg}18`,
                          color: theme.bg,
                          borderBottom: `2px solid ${theme.bg}`,
                        }}
                      >
                        <span className="skill-matrix-skill-header-text">{sk.name}</span>
                      </th>
                    )
                  })
                )}
              </tr>
            </thead>

            <tbody>
              {engineers.length === 0 ? (
                <tr>
                  <td
                    colSpan={1 + allSkillColumns.length}
                    style={{ textAlign: 'center', padding: 40, color: '#9CA3AF' }}
                  >
                    {t('common.noData')}
                  </td>
                </tr>
              ) : (
                engineers.map(eng => {
                  const emp = eng.employee
                  const initials = getInitials(emp.name_ja, emp.name_en)
                  const level = getEngineerLevel(eng.skills)
                  const officeInfo = getOfficeFlag(emp.office_location, t)
                  const isMobilizable = mobilizableSet.has(emp.id)
                  const bgColor = getAvatarColor(emp.name_ja || '')

                  return (
                    <tr key={emp.id} className="skill-matrix-body-row">
                      {/* エンジニア情報セル（固定列） */}
                      <td className="skill-matrix-engineer-cell">
                        <div className="skill-matrix-engineer-info">
                          <div
                            className="skill-matrix-avatar"
                            style={{ backgroundColor: bgColor }}
                          >
                            {initials}
                          </div>
                          <div className="skill-matrix-engineer-detail">
                            <div className="skill-matrix-engineer-name">
                              {emp.name_en || emp.name_ja}
                            </div>
                            <div className="skill-matrix-engineer-meta">
                              {level && <span className="skill-matrix-level-tag">{level}</span>}
                              <span
                                className="skill-matrix-office-tag"
                                style={{
                                  backgroundColor: `${officeInfo.color}15`,
                                  color: officeInfo.color,
                                  border: `1px solid ${officeInfo.color}40`,
                                }}
                              >
                                <span className="skill-matrix-office-flag">{officeInfo.flag}</span>
                                {' '}{officeInfo.label}
                              </span>
                              {isMobilizable && (
                                <Tooltip title={t('skillMatrix.mobilizable')}>
                                  <span className="skill-matrix-mobilizable">✈</span>
                                </Tooltip>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* スキルセル */}
                      {allSkillColumns.map(sk => {
                        const entry = eng.skills[sk.id]
                        const lvl = entry?.level

                        if (lvl == null) {
                          return (
                            <td key={sk.id} className="skill-matrix-cell skill-matrix-cell-empty">
                              <span className="skill-matrix-dash">—</span>
                            </td>
                          )
                        }

                        const colors = LEVEL_CELL_COLORS[lvl] ?? LEVEL_CELL_COLORS[1]
                        const tip = entry?.years != null ? `${entry.years}年経験` : undefined

                        return (
                          <td key={sk.id} className="skill-matrix-cell">
                            <Tooltip title={tip}>
                              <div
                                className="skill-matrix-level-badge"
                                style={{
                                  backgroundColor: colors.bg,
                                  color: colors.text,
                                  border: `1px solid ${colors.border}`,
                                }}
                              >
                                <span className="skill-matrix-level-number">{lvl}</span>
                                <span className="skill-matrix-level-stars">{renderStars(lvl)}</span>
                              </div>
                            </Tooltip>
                          </td>
                        )
                      })}
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
