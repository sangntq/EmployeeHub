/**
 * 資格管理概要ページ
 *
 * 全社の資格保有状況をカテゴリ別カード形式で表示する。
 * 期限ステータスのフィルターはクライアントサイドで実装（APIが未対応）。
 */
import { useState, useCallback, useMemo } from 'react'
import {
  Input,
  Select,
  Row,
  Col,
  Avatar,
  Typography,
  Tag,
  Skeleton,
  Card,
  Tooltip,
  Empty,
} from 'antd'
import {
  SearchOutlined,
  UserOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  MinusCircleOutlined,
  SafetyCertificateOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  StarOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import PageHeader from '../../components/common/PageHeader'
import SectionHeader from '../../components/common/SectionHeader'
import KpiCard from '../../components/dashboard/KpiCard'
import { certOverviewApi } from '../../api/certOverview'
import type { CertOverviewItem, CertHolder } from '../../api/certOverview'

const { Option } = Select

const OFFICE_OPTIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const CERT_CATEGORY_OPTIONS = ['LANGUAGE', 'CLOUD', 'PM', 'NETWORK', 'SECURITY', 'OTHER']
const EXPIRY_STATUS_OPTIONS = ['ALL', 'SOON', 'VALID', 'NO_EXPIRY']

/** カテゴリごとのアクセントカラーと絵文字アイコン */
const CATEGORY_CONFIG: Record<string, { color: string; icon: string }> = {
  LANGUAGE: { color: '#3B82F6', icon: '🌐' },
  CLOUD:    { color: '#0EA5E9', icon: '☁️' },
  PM:       { color: '#10B981', icon: '📋' },
  NETWORK:  { color: '#F59E0B', icon: '🔌' },
  SECURITY: { color: '#EF4444', icon: '🔒' },
  OTHER:    { color: '#8B5CF6', icon: '⚙️' },
}

/** アバター背景色 */
const AVATAR_COLORS = [
  '#4F46E5', '#7C3AED', '#DB2777', '#DC2626',
  '#D97706', '#059669', '#0891B2', '#2563EB',
]
function getAvatarColor(name: string): string {
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]
}

/** 資格カードの期限バッジ */
function ExpiryBadge({ item, t }: { item: CertOverviewItem; t: (key: string) => string }) {
  if (!item.has_expiry) {
    return (
      <Tag icon={<MinusCircleOutlined />} color="default" style={{ fontSize: 11 }}>
        {t('certOverview.noExpiryBadge')}
      </Tag>
    )
  }
  if (item.expiring_soon > 0) {
    return (
      <Tag icon={<WarningOutlined />} color="warning" style={{ fontSize: 11 }}>
        {t('certOverview.soonBadge')} ({item.expiring_soon})
      </Tag>
    )
  }
  return (
    <Tag icon={<CheckCircleOutlined />} color="success" style={{ fontSize: 11 }}>
      {t('certOverview.validBadge')}
    </Tag>
  )
}

/** 保有者アバター一覧（最大5名） */
function HolderAvatarGroup({ holders }: { holders: CertHolder[] }) {
  const MAX_SHOWN = 5
  const shown = holders.slice(0, MAX_SHOWN)
  const extra = holders.length - MAX_SHOWN
  return (
    <Avatar.Group maxCount={MAX_SHOWN} size={24}>
      {shown.map(h => (
        <Tooltip key={h.employee_id} title={h.name_ja}>
          <Avatar
            size={24}
            src={h.avatar_url}
            icon={!h.avatar_url ? <UserOutlined /> : undefined}
            style={
              !h.avatar_url
                ? { backgroundColor: getAvatarColor(h.name_ja), color: '#fff', fontSize: 10 }
                : undefined
            }
          >
            {!h.avatar_url ? h.name_ja.charAt(0) : undefined}
          </Avatar>
        </Tooltip>
      ))}
      {extra > 0 && (
        <Avatar size={24} style={{ backgroundColor: '#F3F4F6', color: '#6B7280', fontSize: 10 }}>
          +{extra}
        </Avatar>
      )}
    </Avatar.Group>
  )
}

export default function CertificationsPage() {
  const { t } = useTranslation()

  const [search, setSearch]             = useState('')
  const [location, setLocation]         = useState<string | undefined>()
  const [category, setCategory]         = useState<string | undefined>()
  const [expiryFilter, setExpiryFilter] = useState<string>('ALL')

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
  }, [])

  const params = {
    location: location || undefined,
    category: category || undefined,
    search:   search   || undefined,
  }

  const { data, isLoading } = useQuery({
    queryKey: ['certOverview', params],
    queryFn: () => certOverviewApi.get(params),
    staleTime: 3 * 60 * 1000,
  })

  // クライアントサイドで期限フィルター適用
  const filteredCategories = useMemo(() => {
    if (!data?.categories) return []
    if (expiryFilter === 'ALL') return data.categories
    return data.categories
      .map(cat => ({
        ...cat,
        items: cat.items.filter(item => {
          if (expiryFilter === 'NO_EXPIRY') return !item.has_expiry
          if (expiryFilter === 'SOON')      return item.has_expiry && item.expiring_soon > 0
          if (expiryFilter === 'VALID')     return item.has_expiry && item.expiring_soon === 0
          return true
        }),
      }))
      .filter(cat => cat.items.length > 0)
  }, [data?.categories, expiryFilter])

  // トップカテゴリ（保有者数が最多）
  const topCategory = useMemo(() => {
    if (!data?.categories || data.categories.length === 0) return '—'
    const sorted = [...data.categories].sort((a, b) => b.total_holders - a.total_holders)
    return t(`certCategory.${sorted[0].category}`)
  }, [data?.categories, t])

  return (
    <div>
      <PageHeader title={t('nav.certifications')} />

      {/* ── KPI カード（KpiCard 共通コンポーネント使用） ── */}
      <Row gutter={[12, 12]} style={{ marginBottom: 20 }}>
        <Col xs={24} sm={12} md={6}>
          <KpiCard
            title={t('certOverview.totalCerts')}
            value={isLoading ? '—' : (data?.total_certs ?? 0)}
            icon={<SafetyCertificateOutlined />}
            valueStyle={{ color: '#4F46E5' }}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <KpiCard
            title={t('certOverview.totalHolders')}
            value={isLoading ? '—' : (data?.total_holders ?? 0)}
            icon={<TeamOutlined />}
            valueStyle={{ color: '#059669' }}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <KpiCard
            title={t('certOverview.expiringSoon')}
            value={isLoading ? '—' : (data?.expiring_soon_60d ?? 0)}
            icon={<ClockCircleOutlined />}
            valueStyle={{ color: '#D97706' }}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <KpiCard
            title={t('certOverview.topCategory')}
            value={isLoading ? '—' : topCategory}
            icon={<StarOutlined />}
            valueStyle={{ color: '#7C3AED', fontSize: 20 }}
          />
        </Col>
      </Row>

      {/* ── フィルターバー ── */}
      <Row gutter={[8, 8]} style={{ marginBottom: 20 }}>
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
            placeholder={t('cert.category')}
            allowClear
            style={{ width: 150 }}
            value={category}
            onChange={v => setCategory(v)}
          >
            {CERT_CATEGORY_OPTIONS.map(c => (
              <Option key={c} value={c}>{t(`certCategory.${c}`)}</Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Select
            style={{ width: 140 }}
            value={expiryFilter}
            onChange={v => setExpiryFilter(v)}
          >
            {EXPIRY_STATUS_OPTIONS.map(s => (
              <Option key={s} value={s}>
                {s === 'ALL'      ? t('common.all')
                 : s === 'SOON'  ? t('certOverview.soonBadge')
                 : s === 'VALID' ? t('certOverview.validBadge')
                 :                 t('certOverview.noExpiryBadge')}
              </Option>
            ))}
          </Select>
        </Col>
      </Row>

      {/* ── ローディング ── */}
      {isLoading && <Skeleton active paragraph={{ rows: 12 }} />}

      {/* ── 空状態 ── */}
      {!isLoading && filteredCategories.length === 0 && (
        <Empty description={t('common.noData')} />
      )}

      {/* ── カテゴリ別資格カードグリッド ── */}
      {!isLoading && filteredCategories.map(cat => {
        const cfg = CATEGORY_CONFIG[cat.category] ?? { color: '#4F46E5', icon: '📜' }

        return (
          <div key={cat.category} style={{ marginBottom: 32 }}>
            {/* SectionHeader 共通コンポーネント */}
            <SectionHeader
              title={t(`certCategory.${cat.category}`)}
              icon={cfg.icon}
              accentColor={cfg.color}
              tags={[
                `${cat.cert_count} ${t('certOverview.totalCerts')}`,
                `${cat.total_holders} ${t('common.people')}`,
              ]}
            />

            {/* 資格カードグリッド */}
            <Row gutter={[12, 12]}>
              {cat.items.map((item: CertOverviewItem) => (
                <Col key={item.master_id ?? item.name} xs={24} sm={12} lg={8} xl={6}>
                  <Card
                    size="small"
                    style={{ height: '100%' }}
                    bodyStyle={{ padding: '12px 16px' }}
                  >
                    {/* 資格名 + 発行機関 + 期限バッジ */}
                    <div style={{ marginBottom: 6 }}>
                      <Typography.Text
                        strong
                        style={{ fontSize: 13, display: 'block', marginBottom: 4 }}
                      >
                        {item.name}
                      </Typography.Text>
                      {item.issuer && (
                        <Typography.Text
                          type="secondary"
                          style={{ fontSize: 11, display: 'block', marginBottom: 4 }}
                        >
                          {item.issuer}
                        </Typography.Text>
                      )}
                      <ExpiryBadge item={item} t={t} />
                    </div>

                    {/* 保有者数 + アバターグループ */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginTop: 8,
                        paddingTop: 8,
                        borderTop: '1px solid #F3F4F6',
                      }}
                    >
                      <Typography.Text
                        style={{ fontSize: 12, color: cfg.color, fontWeight: 600 }}
                      >
                        {item.holder_count} {t('common.people')}
                      </Typography.Text>
                      {item.holders.length > 0 && (
                        <HolderAvatarGroup holders={item.holders} />
                      )}
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        )
      })}
    </div>
  )
}
