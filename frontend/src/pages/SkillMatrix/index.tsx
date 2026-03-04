/**
 * スキルマトリクスページ（Multi-level 詳細表示）
 *
 * エンジニアリストを表示し、行を展開するとカテゴリ別スキル詳細＋資格数を表示する。
 * テーブルは画面内スクロールに収まるよう高さを固定する。
 */
import { useState, useCallback, useMemo } from 'react'
import {
  Table,
  Input,
  Select,
  Checkbox,
  Row,
  Col,
  Avatar,
  Typography,
  Tag,
  Skeleton,
  Space,
  Tooltip,
  Rate,
  Divider,
} from 'antd'
import { SearchOutlined, UserOutlined, SafetyCertificateOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import PageHeader from '../../components/common/PageHeader'
import { skillMatrixApi } from '../../api/skillmatrix'
import { certOverviewApi } from '../../api/certOverview'
import { skillsApi } from '../../api/skills'
import type { EngineerRow, SkillMatrixCategory } from '../../api/skillmatrix'

const { Option } = Select

const OFFICE_OPTIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const LEVEL_OPTIONS  = [1, 2, 3, 4, 5]

/** 資格カテゴリごとのバッジ色 */
const CERT_CAT_COLORS: Record<string, string> = {
  LANGUAGE: 'blue',
  CLOUD:    'cyan',
  PM:       'green',
  NETWORK:  'gold',
  SECURITY: 'red',
  OTHER:    'purple',
}

/** スキルレベルごとの色定義 */
const LEVEL_COLORS: Record<number, { bg: string; text: string; border: string }> = {
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
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]
}

/** レベル別スキル数を数える */
function countByLevel(skills: EngineerRow['skills'], ...levels: number[]): number {
  return Object.values(skills).filter(
    e => e.level != null && levels.includes(e.level)
  ).length
}

/**
 * スキルレベルと保有数から 1〜5 の評価スターを計算する
 *
 * ・加重平均レベル (avg) + 保有数ボーナス (0〜0.5) を合算
 * ・5★: エキスパート (score ≥ 4.8)
 * ・4★: シニア       (score ≥ 3.8)
 * ・3★: ミドル       (score ≥ 2.8)
 * ・2★: ジュニア     (score ≥ 1.8)
 * ・1★: 初心者
 */
function calcStars(skills: EngineerRow['skills']): number {
  const entries = Object.values(skills).filter(e => e.level != null)
  if (entries.length === 0) return 0
  const avg = entries.reduce((s, e) => s + e.level!, 0) / entries.length
  const volumeBonus = Math.min(entries.length / 20, 0.5)
  const score = avg + volumeBonus
  if (score >= 4.8) return 5
  if (score >= 3.8) return 4
  if (score >= 2.8) return 3
  if (score >= 1.8) return 2
  return 1
}

/** 展開行：カテゴリ別スキル詳細＋資格数グリッド */
function SkillDetail({
  rec,
  categories,
  empCerts,
  t,
}: {
  rec: EngineerRow
  categories: SkillMatrixCategory[]
  empCerts: Record<string, number>   // category → cert count
  t: (k: string, opts?: object) => string
}) {
  const activeCats = categories.filter(cat =>
    cat.skills.some(sk => rec.skills[sk.id]?.level != null)
  )
  const certEntries = Object.entries(empCerts).filter(([, n]) => n > 0)

  const hasSkills = activeCats.length > 0
  const hasCerts  = certEntries.length > 0

  if (!hasSkills && !hasCerts) {
    return (
      <Typography.Text type="secondary" style={{ paddingLeft: 52, fontSize: 13 }}>
        {t('common.noData')}
      </Typography.Text>
    )
  }

  return (
    <div
      style={{
        padding: '10px 16px 10px 52px',
        background: '#F9FAFB',
        borderTop: '1px solid #E5E7EB',
      }}
    >
      {/* ── スキルセクション ─────────────────────────────────────── */}
      {hasSkills && (
        <>
          <Typography.Text
            style={{
              fontSize: 11,
              fontWeight: 700,
              color: '#4F46E5',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              display: 'block',
              marginBottom: 8,
            }}
          >
            🛠 {t('nav.skills')}
          </Typography.Text>

          {activeCats.map(cat => {
            const catSkills = cat.skills.filter(sk => rec.skills[sk.id]?.level != null)
            return (
              <div key={cat.id} style={{ marginBottom: 10 }}>
                <Typography.Text
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: '#6B7280',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    display: 'block',
                    marginBottom: 4,
                  }}
                >
                  {cat.name_ja}
                </Typography.Text>
                <Space size={[6, 6]} wrap>
                  {catSkills.map(sk => {
                    const entry = rec.skills[sk.id]
                    const level = entry.level!
                    const c = LEVEL_COLORS[level] ?? LEVEL_COLORS[1]
                    const tip = entry.years != null
                      ? `${entry.years}${t('common.years', { count: entry.years })}`
                      : undefined
                    return (
                      <Tooltip key={sk.id} title={tip}>
                        <Tag
                          style={{
                            backgroundColor: c.bg,
                            color: c.text,
                            border: `1px solid ${c.border}`,
                            fontSize: 12,
                            margin: 0,
                            cursor: tip ? 'help' : 'default',
                          }}
                        >
                          {sk.name}&nbsp;<strong>Lv{level}</strong>
                        </Tag>
                      </Tooltip>
                    )
                  })}
                </Space>
              </div>
            )
          })}
        </>
      )}

      {/* ── 資格セクション ─────────────────────────────────────── */}
      {hasCerts && (
        <>
          {hasSkills && <Divider style={{ margin: '8px 0' }} />}
          <Typography.Text
            style={{
              fontSize: 11,
              fontWeight: 700,
              color: '#7C3AED',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              display: 'block',
              marginBottom: 8,
            }}
          >
            <SafetyCertificateOutlined /> {t('nav.certifications')}
          </Typography.Text>
          <Space size={[8, 6]} wrap>
            {certEntries.map(([cat, count]) => (
              <Tag
                key={cat}
                color={CERT_CAT_COLORS[cat] ?? 'default'}
                style={{ fontSize: 12 }}
              >
                {t(`certCategory.${cat}`)}&nbsp;
                <strong>{count}</strong>
              </Tag>
            ))}
          </Space>
        </>
      )}
    </div>
  )
}

export default function SkillMatrixPage() {
  const { t, i18n } = useTranslation()

  const [search, setSearch]         = useState('')
  const [location, setLocation]     = useState<string | undefined>()
  const [levelMin, setLevelMin]     = useState<number | undefined>()
  const [categoryId, setCategoryId] = useState<string | undefined>()
  const [freeOnly, setFreeOnly]     = useState(false)

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

  // スキルマスタ全件（カバレッジ計算用）
  const { data: masterData } = useQuery({
    queryKey: ['skillMasterAll'],
    queryFn:  () => skillsApi.listMasters(),
    staleTime: 10 * 60 * 1000,
  })
  const totalMasterSkills = useMemo(
    () => (masterData?.categories ?? []).reduce((s: number, c: { skills: unknown[] }) => s + c.skills.length, 0),
    [masterData]
  )

  // 資格概要データ（全社員分、フィルターなし）
  const { data: certData } = useQuery({
    queryKey: ['certOverviewAll'],
    queryFn:  () => certOverviewApi.get({}),
    staleTime: 5 * 60 * 1000,
  })

  // 社員ごとのカテゴリ別資格数マップを構築
  // empCertMap[employeeId][category] = count
  const empCertMap = useMemo(() => {
    const map: Record<string, Record<string, number>> = {}
    if (!certData?.categories) return map
    for (const cat of certData.categories) {
      for (const item of cat.items) {
        for (const holder of item.holders) {
          if (!map[holder.employee_id]) map[holder.employee_id] = {}
          map[holder.employee_id][cat.category] =
            (map[holder.employee_id][cat.category] ?? 0) + 1
        }
      }
    }
    return map
  }, [certData?.categories])

  const categories: SkillMatrixCategory[] = data?.categories ?? []
  const engineers:  EngineerRow[]          = data?.engineers  ?? []

  const totalSkills = categories.reduce((acc, cat) => acc + cat.skills.length, 0)

  // 資格保有者の総ユニーク社員数 (KPI)
  const totalCertHolders = useMemo(
    () => Object.keys(empCertMap).length,
    [empCertMap]
  )

  // ── メインテーブル列 ────────────────────────────────────────────────────
  const columns = [
    {
      title: t('availability.engineer'),
      key: 'engineer',
      render: (_: unknown, rec: EngineerRow) => {
        const emp = rec.employee
        const initial = (emp.name_ja || '?').charAt(0)
        return (
          <Space>
            <Avatar
              size={32}
              src={emp.avatar_url}
              icon={!emp.avatar_url ? <UserOutlined /> : undefined}
              style={
                !emp.avatar_url
                  ? { backgroundColor: getAvatarColor(emp.name_ja || ''), color: '#fff' }
                  : undefined
              }
            >
              {!emp.avatar_url ? initial : undefined}
            </Avatar>
            <div>
              <Typography.Text style={{ fontSize: 13, display: 'block', fontWeight: 500 }}>
                {emp.name_ja}
              </Typography.Text>
              <Typography.Text type="secondary" style={{ fontSize: 11 }}>
                {emp.employee_number}
              </Typography.Text>
            </div>
          </Space>
        )
      },
    },
    {
      title: t('common.officeLocation'),
      key: 'office',
      width: 110,
      render: (_: unknown, rec: EngineerRow) => (
        <Tag style={{ fontSize: 11 }}>
          {t(`officeLocation.${rec.employee.office_location}`)}
        </Tag>
      ),
    },
    {
      title: t('nav.department'),
      key: 'dept',
      width: 160,
      render: (_: unknown, rec: EngineerRow) => {
        const dept = rec.employee.department
        const name = i18n.language === 'ja'
          ? dept?.name_ja
          : (dept?.name_en ?? dept?.name_ja)
        return (
          <Typography.Text style={{ fontSize: 12 }} type="secondary">
            {name ?? '—'}
          </Typography.Text>
        )
      },
    },
    {
      title: t('skillMatrix.rating'),
      key: 'stars',
      width: 120,
      align: 'center' as const,
      render: (_: unknown, rec: EngineerRow) => {
        const stars = calcStars(rec.skills)
        return stars > 0
          ? <Rate disabled value={stars} style={{ fontSize: 13 }} />
          : <Typography.Text type="secondary">—</Typography.Text>
      },
    },
    // ── 資格数（カテゴリ別は展開行へ）──────────────────────────────
    {
      title: t('skillMatrix.certCount'),
      key: 'cert_count',
      width: 72,
      align: 'center' as const,
      render: (_: unknown, rec: EngineerRow) => {
        const total = (Object.values(empCertMap[rec.employee.id] ?? {}) as number[])
          .reduce((s: number, n: number) => s + n, 0)
        return total > 0
          ? <Tag color="purple" style={{ fontWeight: 600 }}>{total}</Tag>
          : <Typography.Text type="secondary">—</Typography.Text>
      },
    },
    // ── スキルレベル分布 ──────────────────────────────────────────
    {
      title: 'Lv1–2',
      key: 'lv12',
      width: 60,
      align: 'center' as const,
      render: (_: unknown, rec: EngineerRow) => {
        const n = countByLevel(rec.skills, 1, 2)
        return n > 0
          ? <span style={{ fontSize: 12, color: LEVEL_COLORS[2].text }}>{n}</span>
          : <Typography.Text type="secondary" style={{ fontSize: 12 }}>—</Typography.Text>
      },
    },
    {
      title: 'Lv3',
      key: 'lv3',
      width: 55,
      align: 'center' as const,
      render: (_: unknown, rec: EngineerRow) => {
        const n = countByLevel(rec.skills, 3)
        return n > 0
          ? <span style={{ fontSize: 12, color: LEVEL_COLORS[3].text }}>{n}</span>
          : <Typography.Text type="secondary" style={{ fontSize: 12 }}>—</Typography.Text>
      },
    },
    {
      title: 'Lv4',
      key: 'lv4',
      width: 55,
      align: 'center' as const,
      render: (_: unknown, rec: EngineerRow) => {
        const n = countByLevel(rec.skills, 4)
        return n > 0
          ? <span style={{ fontSize: 12, color: LEVEL_COLORS[4].text, fontWeight: 600 }}>{n}</span>
          : <Typography.Text type="secondary" style={{ fontSize: 12 }}>—</Typography.Text>
      },
    },
    {
      title: 'Lv5',
      key: 'lv5',
      width: 55,
      align: 'center' as const,
      render: (_: unknown, rec: EngineerRow) => {
        const n = countByLevel(rec.skills, 5)
        return n > 0
          ? <span style={{ fontSize: 12, color: LEVEL_COLORS[5].text, fontWeight: 700 }}>{n}</span>
          : <Typography.Text type="secondary" style={{ fontSize: 12 }}>—</Typography.Text>
      },
    },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 80px)' }}>
      <PageHeader title={t('nav.skills')} />

      {/* KPI カード */}
      <Row gutter={[12, 12]} style={{ marginBottom: 14, flexShrink: 0 }}>
        <Col xs={12} md={6}>
          <div style={{ background: '#fff', borderRadius: 8, padding: '10px 16px', borderLeft: '3px solid #4F46E5', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
            <Typography.Text type="secondary" style={{ fontSize: 11 }}>{t('skillMatrix.engineers')}</Typography.Text>
            <div style={{ fontSize: 22, fontWeight: 700, color: '#4F46E5' }}>
              {isLoading ? '—' : engineers.length}
            </div>
          </div>
        </Col>
        <Col xs={12} md={6}>
          <div style={{ background: '#fff', borderRadius: 8, padding: '10px 16px', borderLeft: '3px solid #7C3AED', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
            <Typography.Text type="secondary" style={{ fontSize: 11 }}>{t('skillMatrix.uniqueSkills')}</Typography.Text>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
              <span style={{ fontSize: 22, fontWeight: 700, color: '#7C3AED' }}>
                {isLoading ? '—' : totalSkills}
              </span>
              {!isLoading && totalMasterSkills > 0 && (
                <Typography.Text type="secondary" style={{ fontSize: 13 }}>
                  / {totalMasterSkills}
                </Typography.Text>
              )}
            </div>
          </div>
        </Col>
        <Col xs={12} md={6}>
          <div style={{ background: '#fff', borderRadius: 8, padding: '10px 16px', borderLeft: '3px solid #059669', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
            <Typography.Text type="secondary" style={{ fontSize: 11 }}>{t('skillMatrix.certHolders')}</Typography.Text>
            <div style={{ fontSize: 22, fontWeight: 700, color: '#059669' }}>
              {isLoading ? '—' : totalCertHolders}
            </div>
          </div>
        </Col>
      </Row>

      {/* フィルターバー */}
      <Row gutter={[8, 8]} style={{ marginBottom: 14, flexShrink: 0 }} align="middle">
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
            placeholder={t('nav.department')}
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
          <Checkbox checked={freeOnly} onChange={e => setFreeOnly(e.target.checked)}>
            <Typography.Text style={{ fontSize: 13 }}>
              {t('skillMatrix.freeOnly')}
            </Typography.Text>
          </Checkbox>
        </Col>
      </Row>

      {/* スキルレベル凡例 */}
      <Row gutter={8} style={{ marginBottom: 10, flexShrink: 0 }}>
        {Object.entries(LEVEL_COLORS).map(([level, def]) => (
          <Col key={level}>
            <Space size={4}>
              <div
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: 3,
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
                {level}
              </div>
              <Typography.Text style={{ fontSize: 12 }}>
                {t(`skillLevel.level${level}`)}
              </Typography.Text>
            </Space>
          </Col>
        ))}
        <Col flex="auto" />
        <Col>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            💡 {t('skillMatrix.expandHint')}
          </Typography.Text>
        </Col>
      </Row>

      {/* スキルマトリクステーブル（画面内スクロール） */}
      {isLoading ? (
        <Skeleton active paragraph={{ rows: 10 }} />
      ) : (
        <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
          <Table<EngineerRow>
            rowKey={rec => rec.employee.id}
            columns={columns}
            dataSource={engineers}
            pagination={{ pageSize: 50, showSizeChanger: false, hideOnSinglePage: true }}
            scroll={{ y: 'calc(100vh - 440px)' }}
            size="small"
            locale={{ emptyText: t('common.noData') }}
            expandable={{
              expandedRowRender: rec => (
                <SkillDetail
                  rec={rec}
                  categories={categories}
                  empCerts={empCertMap[rec.employee.id] ?? {}}
                  t={t}
                />
              ),
              rowExpandable: rec =>
                Object.values(rec.skills).some(e => e.level != null) ||
                Object.keys(empCertMap[rec.employee.id] ?? {}).length > 0,
            }}
          />
        </div>
      )}
    </div>
  )
}
