/**
 * ダッシュボードページ (S-02)
 *
 * KPIカード・稼働率グラフ・フリー予測・スキル分布・アラートサマリーを表示する。
 * manager以上のロールのみ閲覧可能。
 */
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { Alert, Button, Card, Col, List, Row, Segmented, Skeleton, Typography } from 'antd'
import {
  TeamOutlined,
  CheckCircleOutlined,
  UserOutlined,
  ClockCircleOutlined,
  BellOutlined,
  GlobalOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { dashboardApi } from '../../api/dashboard'
import KpiCard from '../../components/dashboard/KpiCard'
import UtilizationChart from '../../components/dashboard/UtilizationChart'
import FreeForecastChart from '../../components/dashboard/FreeForecastChart'
import SkillsBarChart from '../../components/dashboard/SkillsBarChart'
import SkillHeatmapChart from '../../components/dashboard/SkillHeatmapChart'
import HeadcountTrendChart from '../../components/dashboard/HeadcountTrendChart'
import LocationDonutChart from '../../components/dashboard/LocationDonutChart'
import PageHeader from '../../components/common/PageHeader'

const DASHBOARD_ROLES = ['manager', 'department_head', 'director', 'admin']
const STALE_TIME = 5 * 60 * 1000 // 5分

export default function DashboardPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const [locationTab, setLocationTab] = useState<'all' | 'JP' | 'VN'>('all')

  const hasAccess = user?.systemRole != null && DASHBOARD_ROLES.includes(user.systemRole)

  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: dashboardApi.getOverview,
    staleTime: STALE_TIME,
    enabled: hasAccess,
  })

  const { data: trend, isLoading: loadingTrend } = useQuery({
    queryKey: ['dashboard', 'utilization-trend'],
    queryFn: () => dashboardApi.getUtilizationTrend(6),
    staleTime: STALE_TIME,
    enabled: hasAccess,
  })

  const { data: forecast, isLoading: loadingForecast } = useQuery({
    queryKey: ['dashboard', 'free-forecast'],
    queryFn: dashboardApi.getFreeForecast,
    staleTime: STALE_TIME,
    enabled: hasAccess,
  })

  const { data: skills, isLoading: loadingSkills } = useQuery({
    queryKey: ['dashboard', 'skills-distribution'],
    queryFn: dashboardApi.getSkillsDistribution,
    staleTime: STALE_TIME,
    enabled: hasAccess,
  })

  const { data: heatmap, isLoading: loadingHeatmap } = useQuery({
    queryKey: ['dashboard', 'skill-heatmap'],
    queryFn: dashboardApi.getSkillHeatmap,
    staleTime: STALE_TIME,
    enabled: hasAccess,
  })

  const { data: headcountTrend, isLoading: loadingHeadcount } = useQuery({
    queryKey: ['dashboard', 'headcount-trend'],
    queryFn: () => dashboardApi.getHeadcountTrend(12),
    staleTime: STALE_TIME,
    enabled: hasAccess,
  })

  const { data: locationDist, isLoading: loadingLocation } = useQuery({
    queryKey: ['dashboard', 'location-distribution'],
    queryFn: dashboardApi.getLocationDistribution,
    staleTime: STALE_TIME,
    enabled: hasAccess,
  })

  const { data: mobilizable, isLoading: loadingMobilizable } = useQuery({
    queryKey: ['dashboard', 'mobilizable'],
    queryFn: dashboardApi.getMobilizable,
    staleTime: STALE_TIME,
    enabled: hasAccess,
  })

  if (!hasAccess) {
    return (
      <div>
        <PageHeader title={t('dashboard.title')} />
        <Alert type="warning" showIcon message={t('dashboard.accessDenied')} />
      </div>
    )
  }

  const totalFree = (overview?.free_immediate ?? 0) + (overview?.free_planned ?? 0)
  const freeSubtitle = `${t('dashboard.freeImmediate', { count: overview?.free_immediate ?? 0 })} / ${t('dashboard.freePlanned', { count: overview?.free_planned ?? 0 })}`

  return (
    <div>
      <PageHeader title={t('dashboard.title')} />

      {/* 拠点フィルタータブ */}
      <div style={{ marginBottom: 16 }}>
        <Segmented
          value={locationTab}
          onChange={v => setLocationTab(v as 'all' | 'JP' | 'VN')}
          options={[
            { value: 'all', label: `🌐 ${t('dashboard.locationAll')}` },
            { value: 'JP', label: `🇯🇵 ${t('dashboard.locationJP')}` },
            { value: 'VN', label: `🇻🇳 ${t('dashboard.locationVN')}` },
          ]}
        />
      </div>

      {/* KPIカード行 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          {loadingOverview ? (
            <Card size="small"><Skeleton active paragraph={{ rows: 2 }} /></Card>
          ) : (
            <KpiCard
              title={t('dashboard.totalEmployees')}
              value={overview?.total_employees ?? 0}
              suffix={t('common.people')}
              icon={<TeamOutlined />}
            />
          )}
        </Col>
        <Col xs={24} sm={12} lg={6}>
          {loadingOverview ? (
            <Card size="small"><Skeleton active paragraph={{ rows: 2 }} /></Card>
          ) : (
            <KpiCard
              title={t('dashboard.assigned')}
              value={overview?.assigned ?? 0}
              suffix={t('common.people')}
              extra={
                <Typography.Text type="secondary">
                  {t('dashboard.utilizationRate')}: {overview?.utilization_rate.toFixed(1) ?? 0}%
                </Typography.Text>
              }
              icon={<CheckCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          )}
        </Col>
        <Col xs={24} sm={12} lg={6}>
          {loadingOverview ? (
            <Card size="small"><Skeleton active paragraph={{ rows: 2 }} /></Card>
          ) : (
            <KpiCard
              title={t('dashboard.free')}
              value={totalFree}
              suffix={t('common.people')}
              extra={<Typography.Text type="secondary">{freeSubtitle}</Typography.Text>}
              icon={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          )}
        </Col>
        <Col xs={24} sm={12} lg={6}>
          {loadingOverview ? (
            <Card size="small"><Skeleton active paragraph={{ rows: 2 }} /></Card>
          ) : (
            <KpiCard
              title={t('dashboard.pendingApprovals')}
              value={overview?.pending_approvals ?? 0}
              suffix={t('common.people')}
              icon={<ClockCircleOutlined />}
              valueStyle={overview?.pending_approvals ? { color: '#faad14' } : undefined}
              onClick={() => navigate('/approvals')}
            />
          )}
        </Col>
      </Row>

      {/* モバイル可能者カード（HANOI/HCMC）*/}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} lg={6}>
          {loadingMobilizable ? (
            <Card size="small"><Skeleton active paragraph={{ rows: 2 }} /></Card>
          ) : (
            <KpiCard
              title={t('dashboard.mobilizable')}
              value={mobilizable?.total ?? 0}
              suffix={t('common.people')}
              extra={
                <Typography.Text type="secondary" style={{ fontSize: 11 }}>
                  ✅ {mobilizable?.valid_visa ?? 0} / ⚠️ {mobilizable?.need_visa ?? 0}
                </Typography.Text>
              }
              icon={<GlobalOutlined />}
              valueStyle={{ color: '#4F46E5' }}
              onClick={() => navigate('/availability')}
            />
          )}
        </Col>
      </Row>

      {/* チャート行 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={14}>
          <Card size="small" title={t('dashboard.utilizationTrend', { months: 6 })}>
            {loadingTrend ? (
              <Skeleton active paragraph={{ rows: 4 }} />
            ) : (
              <UtilizationChart data={trend?.months ?? []} />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card size="small" title={t('dashboard.freeForecast')}>
            {loadingForecast ? (
              <Skeleton active paragraph={{ rows: 4 }} />
            ) : (
              <FreeForecastChart data={forecast?.forecast ?? []} />
            )}
          </Card>
        </Col>
      </Row>

      {/* スキル分布 + アラートサマリー行 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card size="small" title={t('dashboard.skillsDistribution')}>
            {loadingSkills ? (
              <Skeleton active paragraph={{ rows: 5 }} />
            ) : (
              <SkillsBarChart data={skills?.items ?? []} />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card
            size="small"
            title={t('dashboard.alertSummary')}
            extra={
              <Button type="link" size="small" onClick={() => navigate('/alerts')}>
                {t('dashboard.viewAlerts')}
              </Button>
            }
          >
            {loadingOverview ? (
              <Skeleton active paragraph={{ rows: 3 }} />
            ) : (
              <List size="small">
                <List.Item
                  extra={
                    <Typography.Text
                      strong
                      type={overview?.alerts.visa_expiry_30d ? 'danger' : undefined}
                    >
                      {overview?.alerts.visa_expiry_30d ?? 0} {t('common.people')}
                    </Typography.Text>
                  }
                >
                  <List.Item.Meta
                    avatar={<BellOutlined style={{ color: '#faad14' }} />}
                    title={t('notification.VISA_EXPIRY')}
                  />
                </List.Item>
                <List.Item
                  extra={
                    <Typography.Text
                      strong
                      type={overview?.alerts.cert_expiry_30d ? 'danger' : undefined}
                    >
                      {overview?.alerts.cert_expiry_30d ?? 0} {t('common.people')}
                    </Typography.Text>
                  }
                >
                  <List.Item.Meta
                    avatar={<BellOutlined style={{ color: '#faad14' }} />}
                    title={t('notification.CERT_EXPIRY')}
                  />
                </List.Item>
              </List>
            )}
          </Card>
        </Col>
      </Row>

      {/* スキルヒートマップ行（フル幅）*/}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card size="small" title={t('dashboard.skillHeatmap')}>
            {loadingHeatmap ? (
              <Skeleton active paragraph={{ rows: 5 }} />
            ) : (
              <SkillHeatmapChart
                categories={heatmap?.categories ?? []}
                items={heatmap?.items ?? []}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* 入退社トレンド + 拠点別分布行 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={14}>
          <Card size="small" title={t('dashboard.headcountTrend', { months: 12 })}>
            {loadingHeadcount ? (
              <Skeleton active paragraph={{ rows: 5 }} />
            ) : (
              <HeadcountTrendChart data={headcountTrend?.months ?? []} />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card size="small" title={t('dashboard.locationDistribution')}>
            {loadingLocation ? (
              <Skeleton active paragraph={{ rows: 4 }} />
            ) : (
              <LocationDonutChart data={locationDist?.items ?? []} />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
