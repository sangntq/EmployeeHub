import { useState } from 'react'
import {
  Alert,
  Avatar,
  Button,
  Card,
  Col,
  Descriptions,
  Form,
  Input,
  Popconfirm,
  Row,
  Select,
  Skeleton,
  Space,
  Tag,
  Tabs,
  Typography,
  Upload,
  message,
} from 'antd'
import {
  ArrowLeftOutlined,
  DeleteOutlined,
  EditOutlined,
  SaveOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { employeesApi } from '../../../api/employees'
import type { EmployeeCreateData } from '../../../api/employees'
import PageHeader from '../../../components/common/PageHeader'
import { useAuth } from '../../../hooks/useAuth'
import { getAvatarColor, getInitials } from '../../../utils/avatarUtils'
import SkillsTab from './SkillsTab'
import CertificationsTab from './CertificationsTab'
import WorkStatusTab from './WorkStatusTab'
import ProjectsTab from './ProjectsTab'
import VisaTab from './VisaTab'
import NotesTab from './NotesTab'
import type { UploadFile } from 'antd'

const { Option } = Select

export default function EmployeeDetailPage() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { isAdmin, canApprove, user } = useAuth()
  const [editing, setEditing] = useState(false)
  const [form] = Form.useForm()
  const [messageApi, ctx] = message.useMessage()

  const isSelf = user?.id === id

  const { data: emp, isLoading, isError } = useQuery({
    queryKey: ['employee', id],
    queryFn: () => employeesApi.get(id!),
    enabled: !!id,
  })

  const updateMutation = useMutation({
    mutationFn: (values: Partial<EmployeeCreateData> & { is_active?: boolean }) => employeesApi.update(id!, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee', id] })
      setEditing(false)
      messageApi.success(t('common.saved'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const avatarMutation = useMutation({
    mutationFn: (file: File) => employeesApi.uploadAvatar(id!, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee', id] })
      messageApi.success(t('common.saved'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const deleteMutation = useMutation({
    mutationFn: () => employeesApi.delete(id!),
    onSuccess: () => {
      messageApi.success(t('common.saved'))
      navigate('/employees')
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const handleSave = () => {
    form.validateFields().then(values => updateMutation.mutate(values))
  }

  const handleAvatarChange = (info: { file: UploadFile }) => {
    if (info.file.originFileObj) {
      avatarMutation.mutate(info.file.originFileObj)
    }
  }

  if (isLoading) return (
    <div>
      <PageHeader
        title={t('page.employeeDetail')}
        breadcrumbs={[{ title: t('page.employees'), href: '/employees' }, { title: '...' }]}
      />
      <Skeleton active paragraph={{ rows: 8 }} />
    </div>
  )

  if (isError || !emp) return (
    <div>
      <PageHeader
        title={t('page.employeeDetail')}
        breadcrumbs={[{ title: t('page.employees'), href: '/employees' }, { title: '—' }]}
      />
      <Alert type="error" message={t('common.error')} showIcon />
    </div>
  )

  const canEdit = isAdmin() || isSelf

  const basicInfoContent = editing ? (
    <Form form={form} layout="vertical" initialValues={emp}>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="name_ja" label={t('profile.nameJa')} rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="name_en" label={t('profile.nameEn')}>
            <Input />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="name_vi" label={t('profile.nameVi')}>
            <Input />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="email" label={t('auth.email')} rules={[{ required: true, type: 'email' }]}>
            <Input />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="phone" label={t('common.phone')}>
            <Input />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="slack_id" label={t('profile.slackId')}>
            <Input />
          </Form.Item>
        </Col>
        {isAdmin() && (
          <>
            <Col span={12}>
              <Form.Item name="office_location" label={t('common.officeLocation')}>
                <Select>
                  {['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER'].map(o => (
                    <Option key={o} value={o}>{t(`officeLocation.${o}`)}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="work_style" label={t('common.workStyle')}>
                <Select>
                  {['ONSITE', 'REMOTE', 'HYBRID'].map(o => (
                    <Option key={o} value={o}>{t(`workStyle.${o}`)}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="employment_type" label={t('common.employmentType')}>
                <Select>
                  {['FULLTIME', 'CONTRACT', 'FREELANCE'].map(o => (
                    <Option key={o} value={o}>{t(`employmentType.${o}`)}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="system_role" label={t('common.role')}>
                <Select>
                  {['member', 'manager', 'department_head', 'sales', 'director', 'admin'].map(r => (
                    <Option key={r} value={r}>{t(`role.${r}`)}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </>
        )}
      </Row>
    </Form>
  ) : (
    <Descriptions bordered column={2} size="middle">
      <Descriptions.Item label={t('profile.nameJa')}>{emp.name_ja}</Descriptions.Item>
      <Descriptions.Item label={t('profile.nameEn')}>{emp.name_en ?? '—'}</Descriptions.Item>
      <Descriptions.Item label={t('profile.nameVi')}>{emp.name_vi ?? '—'}</Descriptions.Item>
      <Descriptions.Item label={t('auth.email')}>{emp.email}</Descriptions.Item>
      <Descriptions.Item label={t('common.phone')}>{emp.phone ?? '—'}</Descriptions.Item>
      <Descriptions.Item label={t('profile.slackId')}>{emp.slack_id ?? '—'}</Descriptions.Item>
      <Descriptions.Item label={t('common.officeLocation')}>
        {t(`officeLocation.${emp.office_location}`)}
      </Descriptions.Item>
      <Descriptions.Item label={t('common.workStyle')}>
        {t(`workStyle.${emp.work_style}`)}
      </Descriptions.Item>
      <Descriptions.Item label={t('common.employmentType')}>
        {t(`employmentType.${emp.employment_type}`)}
      </Descriptions.Item>
      <Descriptions.Item label={t('common.role')}>
        <Tag>{t(`role.${emp.system_role}`)}</Tag>
      </Descriptions.Item>
      <Descriptions.Item label={t('common.joinedAt')}>{emp.joined_at}</Descriptions.Item>
      <Descriptions.Item label={t('common.employeeNumber')}>{emp.employee_number}</Descriptions.Item>
    </Descriptions>
  )

  const tabs = [
    {
      key: 'basic',
      label: t('page.basicInfo'),
      children: basicInfoContent,
    },
    {
      key: 'skills',
      label: t('page.skills'),
      children: (
        <SkillsTab
          employeeId={id!}
          canApply={isSelf}
          canApprove={canApprove()}
        />
      ),
    },
    {
      key: 'certifications',
      label: t('profile.certifications'),
      children: (
        <CertificationsTab
          employeeId={id!}
          canApply={isSelf}
          canApprove={canApprove()}
        />
      ),
    },
    {
      key: 'projects',
      label: t('page.projects'),
      children: (
        <ProjectsTab
          employeeId={id!}
          canEdit={isSelf || canApprove()}
        />
      ),
    },
    {
      key: 'work_status',
      label: t('page.workStatus'),
      children: (
        <WorkStatusTab
          employeeId={id!}
          canEdit={canApprove()}
        />
      ),
    },
    {
      key: 'visa',
      label: t('profile.visa'),
      children: (
        <VisaTab
          employeeId={id!}
          canView={isSelf || canApprove()}
          canEdit={isAdmin()}
        />
      ),
    },
    {
      key: 'notes',
      label: t('notes.tab'),
      children: (
        <NotesTab
          employeeId={id!}
          canEdit={canApprove()}
        />
      ),
    },
  ]

  return (
    <div>
      {ctx}
      <PageHeader
        title={emp.name_ja}
        breadcrumbs={[
          { title: t('page.employees'), href: '/employees' },
          { title: emp.name_ja },
        ]}
        extra={
          canEdit && (
            <Space>
              {editing ? (
                <>
                  <Button onClick={() => setEditing(false)}>{t('action.cancel')}</Button>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    loading={updateMutation.isPending}
                    onClick={handleSave}
                  >
                    {t('action.save')}
                  </Button>
                </>
              ) : (
                <>
                  <Button icon={<EditOutlined />} onClick={() => setEditing(true)}>
                    {t('action.edit')}
                  </Button>
                  {isAdmin() && emp.is_active && (
                    <Popconfirm
                      title={t('employee.deleteConfirm')}
                      onConfirm={() => deleteMutation.mutate()}
                      okText={t('action.confirm')}
                      cancelText={t('action.cancel')}
                      okButtonProps={{ danger: true }}
                    >
                      <Button
                        danger
                        icon={<DeleteOutlined />}
                        loading={deleteMutation.isPending}
                      >
                        {t('action.delete')}
                      </Button>
                    </Popconfirm>
                  )}
                </>
              )}
            </Space>
          )
        }
      />

      <Row gutter={16}>
        {/* 左パネル: アバター + 基本ステータス */}
        <Col xs={24} md={6}>
          <Card style={{ textAlign: 'center' }}>
            <Avatar
              size={96}
              src={emp.avatar_url}
              style={{
                marginBottom: 12,
                background: !emp.avatar_url ? getAvatarColor(emp.name_ja) : undefined,
                fontWeight: 700,
                fontSize: 32,
              }}
            >
              {!emp.avatar_url && getInitials(emp.name_ja, emp.name_en)}
            </Avatar>
            {canEdit && (
              <div style={{ marginBottom: 12 }}>
                <Upload
                  accept="image/jpeg,image/png,image/webp"
                  showUploadList={false}
                  beforeUpload={() => false}
                  onChange={handleAvatarChange}
                >
                  <Button size="small" icon={<UploadOutlined />}>
                    {t('action.uploadAvatar')}
                  </Button>
                </Upload>
              </div>
            )}
            <Typography.Title level={5} style={{ margin: 0 }}>
              {emp.name_ja}
            </Typography.Title>
            {emp.name_en && (
              <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                {emp.name_en}
              </Typography.Text>
            )}
            <div style={{ marginTop: 8 }}>
              <Tag color={emp.is_active ? 'green' : 'default'}>
                {emp.is_active ? t('common.active') : t('common.inactive')}
              </Tag>
              <Tag>{t(`role.${emp.system_role}`)}</Tag>
            </div>
          </Card>
        </Col>

        {/* 右パネル: タブ */}
        <Col xs={24} md={18}>
          <Card>
            <Tabs items={tabs} />
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: 12 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/employees')}>
          {t('action.back')}
        </Button>
      </div>
    </div>
  )
}
