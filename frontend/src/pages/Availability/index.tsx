/**
 * 空きカレンダーページ
 *
 * エンジニアの月別稼働状況をガントチャート形式で表示する。
 * フィルター: 検索ワード・拠点・ステータス
 * ナビゲーション: 表示月のオフセット（前後12ヶ月）
 */
import { useState, useCallback } from 'react'
import {
  Table,
  Input,
  Select,
  Row,
  Col,
  Avatar,
  Typography,
  Tag,
  Skeleton,
  Card,
  Space,
  Button,
  Tooltip,
} from 'antd'
import { SearchOutlined, LeftOutlined, RightOutlined, UserOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import PageHeader from '../../components/common/PageHeader'
import { availabilityApi } from '../../api/availability'
import type { AvailabilityMonth, EmployeeAvailability } from '../../api/availability'
import type { EmployeeListItem } from '../../api/employees'

const { Option } = Select

const OFFICE_OPTIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const STATUS_OPTIONS = ['FREE', 'PARTIAL', 'BUSY']

/** 稼働ステータスの色定義 */
const STATUS_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  FREE:    { bg: '#D1FAE5', text: '#065F46', label: 'availability.free' },
  PARTIAL: { bg: '#FEF3C7', text: '#92400E', label: 'availability.partial' },
  BUSY:    { bg: '#FEE2E2', text: '#991B1B', label: 'availability.busy' },
}

/** アバターの背景色（名前のcharCodeに基づく） */
const AVATAR_COLORS = [
  '#4F46E5', '#7C3AED', '#DB2777', '#DC2626',
  '#D97706', '#059669', '#0891B2', '#2563EB',
]

function getAvatarColor(name: string): string {
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]
}

/** YYYY-MM 形式の月ヘッダーを "YYYY年MM月" 表示に変換 */
function formatMonthHeader(month: string, lang: string): string {
  const [year, m] = month.split('-')
  if (lang === 'ja') return `${year}年${m}月`
  return `${year}-${m}`
}

/** 表示中の期間ラベル（例: Mar – Aug 2026）*/
function buildPeriodLabel(monthsHeader: string[]): string {
  if (monthsHeader.length === 0) return ''
  const fmt = (m: string) => {
    const [year, month] = m.split('-')
    const d = new Date(Number(year), Number(month) - 1, 1)
    return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
  }
  return `${fmt(monthsHeader[0])} – ${fmt(monthsHeader[monthsHeader.length - 1])}`
}

export default function AvailabilityPage() {
  const { t, i18n } = useTranslation()

  const [offsetMonths, setOffsetMonths] = useState(0)
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState<string | undefined>()
  const [status, setStatus] = useState<string | undefined>()

  // 検索入力の debounce（onChange で即時更新）
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
  }, [])

  const params = {
    months: 6,
    offset_months: offsetMonths,
    location: location || undefined,
    search: search || undefined,
    status: status || undefined,
  }

  const { data, isLoading } = useQuery({
    queryKey: ['availability', params],
    queryFn: () => availabilityApi.get(params),
    staleTime: 2 * 60 * 1000,
  })

  const monthsHeader = data?.months_header ?? []
  const items = data?.items ?? []

  // KPI: ステータス別カウント（最初の月を基準）
  const countByStatus = (targetStatus: string) =>
    items.filter(item => item.months[0]?.status === targetStatus).length
  const freeCount = countByStatus('FREE')
  const partialCount = countByStatus('PARTIAL')
  const busyCount = countByStatus('BUSY')

  // テーブル列の構築
  const engineerColumn = {
    title: t('availability.engineer'),
    key: 'engineer',
    fixed: 'left' as const,
    width: 220,
    render: (_: unknown, rec: EmployeeAvailability) => {
      const emp: EmployeeListItem = rec.employee
      const initial = (emp.name_ja || '?').charAt(0)
      return (
        <Space>
          <Avatar
            size={32}
            src={emp.avatar_url}
            icon={!emp.avatar_url ? <UserOutlined /> : undefined}
            style={!emp.avatar_url ? { backgroundColor: getAvatarColor(emp.name_ja || ''), color: '#fff' } : undefined}
          >
            {!emp.avatar_url ? initial : undefined}
          </Avatar>
          <Space direction="vertical" size={0}>
            <Typography.Text strong style={{ fontSize: 13 }}>
              {emp.name_ja}
            </Typography.Text>
            <Space size={4}>
              <Tag style={{ fontSize: 10, padding: '0 4px', lineHeight: '16px', margin: 0 }}>
                {t(`officeLocation.${emp.office_location}`)}
              </Tag>
              <Typography.Text type="secondary" style={{ fontSize: 11 }}>
                {emp.employee_number}
              </Typography.Text>
            </Space>
          </Space>
        </Space>
      )
    },
  }

  const monthColumns = monthsHeader.map((month, idx) => ({
    title: formatMonthHeader(month, i18n.language),
    key: `month_${month}`,
    width: 110,
    align: 'center' as const,
    render: (_: unknown, rec: EmployeeAvailability) => {
      const monthData: AvailabilityMonth | undefined = rec.months[idx]
      if (!monthData) return <span style={{ color: '#9CA3AF' }}>—</span>
      const colorDef = STATUS_COLORS[monthData.status] ?? STATUS_COLORS.BUSY
      const alloc = monthData.allocation
      const projectName = monthData.project_name
      return (
        <Tooltip
          title={
            projectName
              ? `${projectName} (${alloc}%)`
              : alloc > 0
              ? `${alloc}%`
              : undefined
          }
        >
          <div
            style={{
              backgroundColor: colorDef.bg,
              color: colorDef.text,
              borderRadius: 4,
              padding: '2px 6px',
              fontSize: 12,
              fontWeight: 500,
              textAlign: 'center',
              cursor: projectName ? 'help' : 'default',
            }}
          >
            {t(colorDef.label)}
            {alloc > 0 && alloc < 100 && (
              <span style={{ marginLeft: 4, opacity: 0.8 }}>({alloc}%)</span>
            )}
          </div>
        </Tooltip>
      )
    },
  }))

  const columns = [engineerColumn, ...monthColumns]

  const periodLabel = buildPeriodLabel(monthsHeader)

  return (
    <div>
      <PageHeader title={t('nav.availability')} />

      {/* KPI カード */}
      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8} md={6}>
          <Card size="small" style={{ borderLeft: '3px solid #D1FAE5' }}>
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {t('availability.totalFree')}
            </Typography.Text>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#065F46' }}>
              {isLoading ? <Skeleton.Input size="small" active /> : freeCount}
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8} md={6}>
          <Card size="small" style={{ borderLeft: '3px solid #D1FAE5' }}>
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {t('availability.free')}
            </Typography.Text>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#065F46' }}>
              {isLoading ? <Skeleton.Input size="small" active /> : freeCount}
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8} md={6}>
          <Card size="small" style={{ borderLeft: '3px solid #FEF3C7' }}>
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {t('availability.partial')}
            </Typography.Text>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#92400E' }}>
              {isLoading ? <Skeleton.Input size="small" active /> : partialCount}
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8} md={6}>
          <Card size="small" style={{ borderLeft: '3px solid #FEE2E2' }}>
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {t('availability.busy')}
            </Typography.Text>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#991B1B' }}>
              {isLoading ? <Skeleton.Input size="small" active /> : busyCount}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 月ナビゲーション */}
      <Row justify="center" align="middle" gutter={8} style={{ marginBottom: 16 }}>
        <Col>
          <Button
            icon={<LeftOutlined />}
            disabled={offsetMonths <= -12}
            onClick={() => setOffsetMonths(o => o - 1)}
          />
        </Col>
        <Col>
          <Typography.Text strong style={{ minWidth: 200, textAlign: 'center', display: 'inline-block' }}>
            {periodLabel || '—'}
          </Typography.Text>
        </Col>
        <Col>
          <Button
            icon={<RightOutlined />}
            disabled={offsetMonths >= 12}
            onClick={() => setOffsetMonths(o => o + 1)}
          />
        </Col>
      </Row>

      {/* フィルターバー */}
      <Row gutter={[8, 8]} style={{ marginBottom: 16 }}>
        <Col flex="240px">
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
              <Option key={o} value={o}>
                {t(`officeLocation.${o}`)}
              </Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Select
            placeholder={t('common.status')}
            allowClear
            style={{ width: 120 }}
            value={status}
            onChange={v => setStatus(v)}
          >
            {STATUS_OPTIONS.map(s => (
              <Option key={s} value={s}>
                {t(`availability.${s.toLowerCase()}`)}
              </Option>
            ))}
          </Select>
        </Col>
      </Row>

      {/* ガントテーブル */}
      {isLoading ? (
        <Skeleton active paragraph={{ rows: 8 }} />
      ) : (
        <Table<EmployeeAvailability>
          rowKey={rec => rec.employee.id}
          columns={columns}
          dataSource={items}
          pagination={{ pageSize: 50, showSizeChanger: false, hideOnSinglePage: true }}
          scroll={{ x: 'max-content' }}
          size="small"
          locale={{ emptyText: t('availability.noData') }}
        />
      )}

      {/* 凡例 */}
      <Row gutter={16} style={{ marginTop: 12 }}>
        <Col>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {t('availability.legend')}:
          </Typography.Text>
        </Col>
        {Object.entries(STATUS_COLORS).map(([key, def]) => (
          <Col key={key}>
            <Space size={4}>
              <div
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: 2,
                  backgroundColor: def.bg,
                  border: `1px solid ${def.text}`,
                  display: 'inline-block',
                }}
              />
              <Typography.Text style={{ fontSize: 12, color: def.text }}>
                {t(def.label)}
              </Typography.Text>
            </Space>
          </Col>
        ))}
      </Row>
    </div>
  )
}
