import { useState } from 'react'
import {
  Table,
  Input,
  Select,
  Button,
  Space,
  Avatar,
  Typography,
  Tag,
  Tooltip,
  Row,
  Col,
  Switch,
  Progress,
} from 'antd'
import {
  SearchOutlined,
  UserAddOutlined,
  UserOutlined,
  AppstoreOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { employeesApi } from '../../../api/employees'
import type { EmployeeListItem, EmployeeListParams } from '../../../api/employees'
import PageHeader from '../../../components/common/PageHeader'
import { useAuth } from '../../../hooks/useAuth'
import EmployeeCard from './EmployeeCard'
import EmployeeDetailPanel from './EmployeeDetailPanel'

const { Option } = Select

const OFFICE_OPTIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const WORK_STYLE_OPTIONS = ['ONSITE', 'REMOTE', 'HYBRID']
const ROLE_OPTIONS = ['member', 'manager', 'department_head', 'sales', 'director', 'admin']

export default function EmployeeListPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { isAdmin } = useAuth()

  const [viewMode, setViewMode] = useState<'table' | 'card'>('table')
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null)

  const [params, setParams] = useState<EmployeeListParams>({
    page: 1,
    per_page: 20,
    is_active: true,
  })

  const { data, isLoading } = useQuery({
    queryKey: ['employees', params],
    queryFn: () => employeesApi.list(params),
  })

  const handleSearch = (keyword: string) =>
    setParams(p => ({ ...p, keyword: keyword || undefined, page: 1 }))

  const columns = [
    {
      title: t('common.name'),
      key: 'name',
      render: (_: unknown, rec: EmployeeListItem) => (
        <Space>
          <Avatar
            size={36}
            src={rec.avatar_url}
            icon={!rec.avatar_url && <UserOutlined />}
            style={{ flexShrink: 0 }}
          />
          <Space direction="vertical" size={0}>
            <Typography.Link
              onClick={e => {
                e.stopPropagation()
                setSelectedEmployeeId(rec.id)
              }}
            >
              {rec.name_ja}
            </Typography.Link>
            {rec.name_en && (
              <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                {rec.name_en}
              </Typography.Text>
            )}
          </Space>
        </Space>
      ),
    },
    {
      title: t('common.employeeNumber'),
      dataIndex: 'employee_number',
      width: 120,
    },
    {
      title: t('nav.department'),
      key: 'department',
      render: (_: unknown, rec: EmployeeListItem) =>
        rec.department ? (
          <Tag>{rec.department.name_ja}</Tag>
        ) : (
          <Typography.Text type="secondary">—</Typography.Text>
        ),
    },
    {
      title: t('common.role'),
      dataIndex: 'system_role',
      width: 120,
      render: (role: string) => <Tag>{t(`role.${role}`)}</Tag>,
    },
    {
      title: t('common.officeLocation'),
      dataIndex: 'office_location',
      width: 100,
      render: (loc: string) => t(`officeLocation.${loc}`),
    },
    {
      title: t('employee.workloadPercent'),
      key: 'workload',
      width: 140,
      render: (_: unknown, rec: EmployeeListItem) =>
        rec.workload_percent != null ? (
          <div style={{ minWidth: 110 }}>
            <div style={{ display: 'flex', justifyContent: 'flex-end', fontSize: 11, marginBottom: 2 }}>
              <span>{rec.workload_percent}%</span>
            </div>
            <Progress
              percent={Math.min(rec.workload_percent, 100)}
              size="small"
              showInfo={false}
              strokeColor={
                rec.workload_percent >= 100
                  ? '#EF4444'
                  : rec.workload_percent >= 50
                    ? '#F59E0B'
                    : '#10B981'
              }
            />
          </div>
        ) : (
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            —
          </Typography.Text>
        ),
    },
    {
      title: '✈️',
      key: 'mobilizable',
      width: 52,
      render: (_: unknown, rec: EmployeeListItem) =>
        rec.is_mobilizable ? (
          <Tooltip title={t('employee.mobilizable')}>
            <span style={{ fontSize: 18 }}>✈️</span>
          </Tooltip>
        ) : null,
    },
    {
      title: t('common.status'),
      dataIndex: 'is_active',
      width: 80,
      render: (active: boolean) =>
        active ? (
          <Tag color="green">{t('common.active')}</Tag>
        ) : (
          <Tag color="default">{t('common.inactive')}</Tag>
        ),
    },
  ]

  return (
    <div>
      <PageHeader
        title={t('page.employees')}
        breadcrumbs={[{ title: t('page.employees') }]}
        extra={
          <Space>
            {/* テーブル/カード切替ボタングループ */}
            <Button.Group>
              <Button
                icon={<UnorderedListOutlined />}
                type={viewMode === 'table' ? 'primary' : 'default'}
                onClick={() => setViewMode('table')}
              />
              <Button
                icon={<AppstoreOutlined />}
                type={viewMode === 'card' ? 'primary' : 'default'}
                onClick={() => setViewMode('card')}
              />
            </Button.Group>
            {isAdmin() && (
              <Button
                type="primary"
                icon={<UserAddOutlined />}
                onClick={() => navigate('/employees/new')}
              >
                {t('action.add')}
              </Button>
            )}
          </Space>
        }
      />

      {/* フィルター */}
      <Row gutter={[8, 8]} style={{ marginBottom: 16 }}>
        <Col flex="240px">
          <Input.Search
            placeholder={t('common.searchPlaceholder')}
            allowClear
            onSearch={handleSearch}
            prefix={<SearchOutlined />}
          />
        </Col>
        <Col>
          <Select
            placeholder={t('common.officeLocation')}
            allowClear
            style={{ width: 120 }}
            onChange={v => setParams(p => ({ ...p, office_location: v, page: 1 }))}
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
            placeholder={t('common.workStyle')}
            allowClear
            style={{ width: 110 }}
            onChange={v => setParams(p => ({ ...p, work_style: v, page: 1 }))}
          >
            {WORK_STYLE_OPTIONS.map(o => (
              <Option key={o} value={o}>
                {t(`workStyle.${o}`)}
              </Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Select
            placeholder={t('common.role')}
            allowClear
            style={{ width: 130 }}
            onChange={v => setParams(p => ({ ...p, system_role: v, page: 1 }))}
          >
            {ROLE_OPTIONS.map(r => (
              <Option key={r} value={r}>
                {t(`role.${r}`)}
              </Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Space>
            <Switch
              checked={params.is_active}
              onChange={v => setParams(p => ({ ...p, is_active: v, page: 1 }))}
            />
            <Typography.Text style={{ fontSize: 13 }}>{t('common.activeOnly')}</Typography.Text>
          </Space>
        </Col>
      </Row>

      {/* テーブルビュー */}
      {viewMode === 'table' && (
        <Table<EmployeeListItem>
          rowKey="id"
          columns={columns}
          dataSource={data?.items ?? []}
          loading={isLoading}
          pagination={{
            current: params.page,
            pageSize: params.per_page,
            total: data?.total ?? 0,
            showSizeChanger: true,
            showTotal: total => `${total} ${t('common.people')}`,
            onChange: (page, per_page) => setParams(p => ({ ...p, page, per_page })),
          }}
          onRow={rec => ({
            onClick: () => setSelectedEmployeeId(rec.id),
            style: { cursor: 'pointer' },
          })}
          size="middle"
        />
      )}

      {/* カードビュー */}
      {viewMode === 'card' && (
        <div>
          <Row gutter={[12, 12]}>
            {(data?.items ?? []).map(emp => (
              <Col key={emp.id} xs={24} sm={12} lg={8} xl={6}>
                <EmployeeCard employee={emp} onClick={() => setSelectedEmployeeId(emp.id)} />
              </Col>
            ))}
          </Row>
          <div style={{ textAlign: 'right', marginTop: 16 }}>
            <Space>
              <Typography.Text type="secondary">
                {data?.total ?? 0} {t('common.people')}
              </Typography.Text>
              <Button
                disabled={(params.page ?? 1) <= 1}
                onClick={() => setParams(p => ({ ...p, page: (p.page ?? 1) - 1 }))}
              >
                {'<'}
              </Button>
              <Typography.Text>
                {params.page} / {Math.max(1, Math.ceil((data?.total ?? 0) / (params.per_page ?? 20)))}
              </Typography.Text>
              <Button
                disabled={
                  (params.page ?? 1) >=
                  Math.max(1, Math.ceil((data?.total ?? 0) / (params.per_page ?? 20)))
                }
                onClick={() => setParams(p => ({ ...p, page: (p.page ?? 1) + 1 }))}
              >
                {'>'}
              </Button>
            </Space>
          </div>
        </div>
      )}

      {/* スライドアウト詳細パネル */}
      <EmployeeDetailPanel
        employeeId={selectedEmployeeId}
        onClose={() => setSelectedEmployeeId(null)}
      />
    </div>
  )
}
