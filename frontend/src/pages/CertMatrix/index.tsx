/**
 * 資格マトリクスページ（グリッド表示）
 *
 * 行＝エンジニア、列＝資格（カテゴリグループ別ヘッダー）。
 * 各セルは資格保有の有無（取得日・期限ステータス）を表示する。
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
import { certMatrixApi } from '../../api/certmatrix'
import type { CertEngineerRow, CertMatrixCategory } from '../../api/certmatrix'

import './style.css'

const { Option } = Select

const OFFICE_OPTIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const CERT_CATEGORIES = ['LANGUAGE', 'CLOUD', 'PM', 'NETWORK', 'SECURITY', 'OTHER']

/** カテゴリヘッダーの色テーマ */
const CATEGORY_THEMES: Record<string, { bg: string; text: string }> = {
  LANGUAGE: { bg: '#2563EB', text: '#fff' },
  CLOUD:    { bg: '#0891B2', text: '#fff' },
  PM:       { bg: '#059669', text: '#fff' },
  NETWORK:  { bg: '#D97706', text: '#fff' },
  SECURITY: { bg: '#DC2626', text: '#fff' },
  OTHER:    { bg: '#7C3AED', text: '#fff' },
}

function getCategoryTheme(category: string) {
  return CATEGORY_THEMES[category] ?? { bg: '#4B5563', text: '#fff' }
}

/** 期限ステータスの色 */
const EXPIRY_COLORS: Record<string, { bg: string; text: string; border: string; label: string }> = {
  VALID:     { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7', label: '✓' },
  SOON:      { bg: '#FEE2E2', text: '#991B1B', border: '#FCA5A5', label: '⚠' },
  NO_EXPIRY: { bg: '#DBEAFE', text: '#1E40AF', border: '#93C5FD', label: '✓' },
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

/** スキルレベルからエンジニアレベルラベルを返す（資格数ベース） */
function getEngineerCertLevel(certs: CertEngineerRow['certs']): string {
  const count = Object.keys(certs).length
  if (count >= 5) return 'Expert'
  if (count >= 3) return 'Senior'
  if (count >= 1) return 'Middle'
  return ''
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

export default function CertMatrixPage() {
  const { t } = useTranslation()
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  const [search, setSearch]       = useState('')
  const [location, setLocation]   = useState<string | undefined>()
  const [category, setCategory]   = useState<string | undefined>()
  const [freeOnly, setFreeOnly]   = useState(false)
  const [certFilter, setCertFilter] = useState<string[]>([])

  const handleSearchChange = useCallback((e: { target: { value: string } }) => {
    setSearch(e.target.value)
  }, [])

  const params = {
    search:    search    || undefined,
    location:  location  || undefined,
    category:  category  || undefined,
    free_only: freeOnly  || undefined,
  }

  const { data, isLoading } = useQuery({
    queryKey: ['certMatrix', params],
    queryFn:  () => certMatrixApi.get(params),
    staleTime: 3 * 60 * 1000,
  })

  const categories: CertMatrixCategory[] = data?.categories ?? []
  const engineers:  CertEngineerRow[]     = data?.engineers  ?? []

  // 資格フィルター適用後のカテゴリ
  const visibleCategories = useMemo(() => {
    const filterSet = new Set(certFilter)
    return categories
      .map(cat => {
        if (filterSet.size === 0) return cat
        const filtered = cat.certifications.filter(c => filterSet.has(c.id))
        return { ...cat, certifications: filtered }
      })
      .filter(cat => cat.certifications.length > 0)
  }, [categories, certFilter])

  // 全資格列のフラットリスト
  const allCertColumns = useMemo(() => {
    return visibleCategories.flatMap(cat => cat.certifications)
  }, [visibleCategories])

  // 資格フィルター用の選択肢（全資格一覧）
  const allCertOptions = useMemo(() => {
    return categories.flatMap(cat =>
      cat.certifications.map(c => ({ value: c.id, label: c.name, category: cat.category }))
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
      <PageHeader title={t('certMatrix.title')} />

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
            placeholder={t('certMatrix.category')}
            allowClear
            style={{ width: 150 }}
            value={category}
            onChange={v => setCategory(v)}
          >
            {CERT_CATEGORIES.map(c => (
              <Option key={c} value={c}>{t(`certCategory.${c}`)}</Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Select
            mode="multiple"
            placeholder={t('certMatrix.certFilter')}
            allowClear
            style={{ minWidth: 180, maxWidth: 350 }}
            maxTagCount={2}
            value={certFilter}
            onChange={v => setCertFilter(v)}
            options={allCertOptions}
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

      {/* 凡例 */}
      <Row gutter={12} style={{ marginBottom: 10, flexShrink: 0 }} align="middle">
        {Object.entries(EXPIRY_COLORS).map(([status, def]) => (
          <Col key={status}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <div
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: 4,
                  backgroundColor: def.bg,
                  border: `1px solid ${def.border}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 11,
                  fontWeight: 700,
                  color: def.text,
                }}
              >
                {def.label}
              </div>
              <Typography.Text style={{ fontSize: 12 }}>
                {t(`certMatrix.expiry_${status}`)}
              </Typography.Text>
            </div>
          </Col>
        ))}
      </Row>

      {/* マトリクステーブル */}
      {isLoading ? (
        <Skeleton active paragraph={{ rows: 12 }} />
      ) : (
        <div
          ref={scrollContainerRef}
          className="cert-matrix-scroll"
          style={{ flex: 1, overflow: 'auto', minHeight: 0 }}
        >
          <table className="cert-matrix-table">
            {/* ── カテゴリグループヘッダー行 ── */}
            <thead>
              <tr className="cert-matrix-cat-row">
                <th
                  className="cert-matrix-engineer-header"
                  rowSpan={2}
                >
                  {t('certMatrix.engineer')}
                </th>
                {visibleCategories.map(cat => {
                  const theme = getCategoryTheme(cat.category)
                  return (
                    <th
                      key={cat.category}
                      colSpan={cat.certifications.length}
                      className="cert-matrix-cat-header"
                      style={{
                        backgroundColor: theme.bg,
                        color: theme.text,
                      }}
                    >
                      {t(`certCategory.${cat.category}`)}
                    </th>
                  )
                })}
              </tr>
              {/* ── 個別資格ヘッダー行 ── */}
              <tr className="cert-matrix-cert-row">
                {visibleCategories.map(cat =>
                  cat.certifications.map(cert => {
                    const theme = getCategoryTheme(cat.category)
                    return (
                      <th
                        key={cert.id}
                        className="cert-matrix-cert-header"
                        style={{
                          backgroundColor: `${theme.bg}18`,
                          color: theme.bg,
                          borderBottom: `2px solid ${theme.bg}`,
                        }}
                      >
                        <Tooltip title={cert.name}>
                          <span className="cert-matrix-cert-header-text">{cert.name}</span>
                        </Tooltip>
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
                    colSpan={1 + allCertColumns.length}
                    style={{ textAlign: 'center', padding: 40, color: '#9CA3AF' }}
                  >
                    {t('common.noData')}
                  </td>
                </tr>
              ) : (
                engineers.map(eng => {
                  const emp = eng.employee
                  const initials = getInitials(emp.name_ja, emp.name_en)
                  const level = getEngineerCertLevel(eng.certs)
                  const officeInfo = getOfficeFlag(emp.office_location, t)
                  const isMobilizable = mobilizableSet.has(emp.id)
                  const bgColor = getAvatarColor(emp.name_ja || '')

                  return (
                    <tr key={emp.id} className="cert-matrix-body-row">
                      {/* エンジニア情報セル（固定列） */}
                      <td className="cert-matrix-engineer-cell">
                        <div className="cert-matrix-engineer-info">
                          <div
                            className="cert-matrix-avatar"
                            style={{ backgroundColor: bgColor }}
                          >
                            {initials}
                          </div>
                          <div className="cert-matrix-engineer-detail">
                            <div className="cert-matrix-engineer-name">
                              {emp.name_en || emp.name_ja}
                            </div>
                            <div className="cert-matrix-engineer-meta">
                              {level && <span className="cert-matrix-level-tag">{level}</span>}
                              <span
                                className="cert-matrix-office-tag"
                                style={{
                                  backgroundColor: `${officeInfo.color}15`,
                                  color: officeInfo.color,
                                  border: `1px solid ${officeInfo.color}40`,
                                }}
                              >
                                <span className="cert-matrix-office-flag">{officeInfo.flag}</span>
                                {' '}{officeInfo.label}
                              </span>
                              {isMobilizable && (
                                <Tooltip title={t('skillMatrix.mobilizable')}>
                                  <span className="cert-matrix-mobilizable">✈</span>
                                </Tooltip>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* 資格セル */}
                      {allCertColumns.map(cert => {
                        const entry = eng.certs[cert.id]

                        if (!entry) {
                          return (
                            <td key={cert.id} className="cert-matrix-cell cert-matrix-cell-empty">
                              <span className="cert-matrix-dash">—</span>
                            </td>
                          )
                        }

                        const status = entry.expiry_status || 'NO_EXPIRY'
                        const colors = EXPIRY_COLORS[status] ?? EXPIRY_COLORS.VALID
                        const tipLines: string[] = []
                        if (entry.obtained_at) tipLines.push(`${t('certMatrix.obtained')}: ${entry.obtained_at}`)
                        if (entry.expires_at) tipLines.push(`${t('certMatrix.expires')}: ${entry.expires_at}`)
                        const tip = tipLines.join('\n') || cert.name

                        return (
                          <td key={cert.id} className="cert-matrix-cell">
                            <Tooltip title={<span style={{ whiteSpace: 'pre-line' }}>{tip}</span>}>
                              <div
                                className="cert-matrix-cert-badge"
                                style={{
                                  backgroundColor: colors.bg,
                                  color: colors.text,
                                  border: `1px solid ${colors.border}`,
                                }}
                              >
                                <span className="cert-matrix-cert-icon">{colors.label}</span>
                                {entry.obtained_at && (
                                  <span className="cert-matrix-cert-year">
                                    {entry.obtained_at.substring(0, 4)}
                                  </span>
                                )}
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
