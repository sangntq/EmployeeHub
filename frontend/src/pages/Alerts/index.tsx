/**
 * アラートダッシュボードページ (S-08)
 *
 * ビザ期限・資格期限の期限切れアラートを一覧表示する。
 * manager以上のロールのみ閲覧可能。
 */
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { Table, Tabs, Tag, Button, Typography } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useNavigate } from 'react-router-dom'
import { dashboardApi } from '../../api/dashboard'
import type { AlertItem } from '../../api/dashboard'
import PageHeader from '../../components/common/PageHeader'

const STALE_TIME = 5 * 60 * 1000 // 5分

export default function AlertsPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const { data, isLoading } = useQuery({
    queryKey: ['alerts', 'all'],
    queryFn: () => dashboardApi.getAlerts(undefined, 30),
    staleTime: STALE_TIME,
  })

  const allItems = data?.items ?? []
  const visaItems = allItems.filter(a => a.type === 'VISA_EXPIRY')
  const certItems = allItems.filter(a => a.type === 'CERT_EXPIRY')

  const columns: ColumnsType<AlertItem> = [
    {
      title: t('alertPage.daysRemaining'),
      dataIndex: 'days_remaining',
      key: 'days_remaining',
      width: 100,
      render: (days: number) => (
        <Tag color={days <= 7 ? 'red' : 'orange'}>
          {t('alertPage.daysRemaining', { days })}
        </Tag>
      ),
      sorter: (a, b) => a.days_remaining - b.days_remaining,
      defaultSortOrder: 'ascend',
    },
    {
      title: t('common.name'),
      key: 'employee',
      render: (_: unknown, record: AlertItem) => (
        <Typography.Text>{record.employee.name_ja}</Typography.Text>
      ),
    },
    {
      title: t('common.employeeNumber'),
      key: 'employee_number',
      render: (_: unknown, record: AlertItem) => (
        <Typography.Text type="secondary">{record.employee.employee_number}</Typography.Text>
      ),
    },
    {
      title: t('alertPage.expiresAt'),
      dataIndex: 'expires_at',
      key: 'expires_at',
      render: (v: string) => v,
    },
    {
      title: '',
      key: 'action',
      width: 120,
      render: (_: unknown, record: AlertItem) => (
        <Button
          type="link"
          size="small"
          onClick={() => navigate(`/employees/${record.employee.id}`)}
        >
          {t('alertPage.openProfile')}
        </Button>
      ),
    },
  ]

  const tabItems = [
    {
      key: 'visa',
      label: t('alertPage.visaExpiry', { count: visaItems.length }),
      children: (
        <Table<AlertItem>
          columns={columns}
          dataSource={visaItems}
          rowKey={r => r.employee.id + '-visa'}
          loading={isLoading}
          size="small"
          locale={{ emptyText: t('alertPage.noAlerts') }}
          pagination={false}
        />
      ),
    },
    {
      key: 'cert',
      label: t('alertPage.certExpiry', { count: certItems.length }),
      children: (
        <Table<AlertItem>
          columns={columns}
          dataSource={certItems}
          rowKey={r => r.employee.id + '-cert'}
          loading={isLoading}
          size="small"
          locale={{ emptyText: t('alertPage.noAlerts') }}
          pagination={false}
        />
      ),
    },
  ]

  return (
    <div>
      <PageHeader title={t('alertPage.title')} />
      <Tabs items={tabItems} />
    </div>
  )
}
