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
} from 'antd'
import { SearchOutlined, UserAddOutlined, UserOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { employeesApi } from '../../../api/employees'
import type { EmployeeListItem, EmployeeListParams } from '../../../api/employees'
import PageHeader from '../../../components/common/PageHeader'
import { useAuth } from '../../../hooks/useAuth'

const { Option } = Select

const OFFICE_OPTIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const WORK_STYLE_OPTIONS = ['ONSITE', 'REMOTE', 'HYBRID']
const ROLE_OPTIONS = ['member', 'manager', 'department_head', 'sales', 'director', 'admin']

export default function EmployeeListPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { isAdmin } = useAuth()

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
            <Typography.Link onClick={() => navigate(`/employees/${rec.id}`)}>
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
      title: t('common.workStyle'),
      dataIndex: 'work_style',
      width: 90,
      render: (ws: string) => t(`workStyle.${ws}`),
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
    {
      title: '',
      key: 'action',
      width: 60,
      render: (_: unknown, rec: EmployeeListItem) => (
        <Tooltip title={t('action.view')}>
          <Button
            type="text"
            size="small"
            onClick={() => navigate(`/employees/${rec.id}`)}
          >
            {t('action.view')}
          </Button>
        </Tooltip>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title={t('page.employees')}
        breadcrumbs={[{ title: t('page.employees') }]}
        extra={
          isAdmin() && (
            <Button
              type="primary"
              icon={<UserAddOutlined />}
              onClick={() => navigate('/employees/new')}
            >
              {t('action.add')}
            </Button>
          )
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
        onRow={rec => ({ onClick: () => navigate(`/employees/${rec.id}`), style: { cursor: 'pointer' } })}
        size="middle"
      />
    </div>
  )
}
