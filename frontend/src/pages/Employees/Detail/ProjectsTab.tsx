import { useState } from 'react'
import {
  Button,
  Card,
  DatePicker,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Tag,
  Typography,
  message,
} from 'antd'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import dayjs from 'dayjs'
import { projectsApi } from '../../../api/projects'
import type { EmployeeProjectItem } from '../../../api/projects'

const PROJECT_ROLES = ['PL', 'PM', 'SE', 'PG', 'QA', 'INFRA', 'DESIGNER', 'OTHER']

interface Props {
  employeeId: string
  canEdit: boolean  // 本人 or manager以上
}

export default function ProjectsTab({ employeeId, canEdit }: Props) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [messageApi, ctx] = message.useMessage()
  const [addOpen, setAddOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<EmployeeProjectItem | null>(null)
  const [form] = Form.useForm()

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['employee-projects', employeeId],
    queryFn: () => projectsApi.listProjects(employeeId),
  })

  const addMutation = useMutation({
    mutationFn: (values: {
      project_name: string
      client_name?: string
      industry?: string
      role: string
      started_at: dayjs.Dayjs
      ended_at?: dayjs.Dayjs
      tech_stack_input?: string
      team_size?: number
      responsibilities?: string
      achievements?: string
    }) =>
      projectsApi.addProject(employeeId, {
        project_name: values.project_name,
        client_name: values.client_name,
        industry: values.industry,
        role: values.role,
        started_at: values.started_at.format('YYYY-MM-DD'),
        ended_at: values.ended_at ? values.ended_at.format('YYYY-MM-DD') : null,
        tech_stack: values.tech_stack_input
          ? values.tech_stack_input.split(',').map(s => s.trim()).filter(Boolean)
          : null,
        team_size: values.team_size,
        responsibilities: values.responsibilities,
        achievements: values.achievements,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-projects', employeeId] })
      setAddOpen(false)
      form.resetFields()
      messageApi.success(t('common.saved'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const editMutation = useMutation({
    mutationFn: (values: {
      project_name?: string
      client_name?: string
      industry?: string
      role?: string
      started_at?: dayjs.Dayjs
      ended_at?: dayjs.Dayjs
      tech_stack_input?: string
      team_size?: number
      responsibilities?: string
      achievements?: string
    }) =>
      projectsApi.updateProject(editTarget!.id, {
        project_name: values.project_name,
        client_name: values.client_name,
        industry: values.industry,
        role: values.role,
        started_at: values.started_at ? values.started_at.format('YYYY-MM-DD') : undefined,
        ended_at: values.ended_at ? values.ended_at.format('YYYY-MM-DD') : null,
        tech_stack: values.tech_stack_input
          ? values.tech_stack_input.split(',').map(s => s.trim()).filter(Boolean)
          : null,
        team_size: values.team_size,
        responsibilities: values.responsibilities,
        achievements: values.achievements,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-projects', employeeId] })
      setEditTarget(null)
      form.resetFields()
      messageApi.success(t('common.saved'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const deleteMutation = useMutation({
    mutationFn: (projectId: string) => projectsApi.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-projects', employeeId] })
      messageApi.success(t('common.saved'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const handleOpenEdit = (proj: EmployeeProjectItem) => {
    form.setFieldsValue({
      project_name: proj.project.name,
      client_name: proj.project.client_name,
      industry: proj.project.industry,
      role: proj.role,
      started_at: dayjs(proj.started_at),
      ended_at: proj.ended_at ? dayjs(proj.ended_at) : undefined,
      tech_stack_input: proj.tech_stack ? proj.tech_stack.join(', ') : '',
      team_size: proj.team_size,
      responsibilities: proj.responsibilities,
      achievements: proj.achievements,
    })
    setEditTarget(proj)
  }

  const handleCloseModal = () => {
    setAddOpen(false)
    setEditTarget(null)
    form.resetFields()
  }

  const isModalOpen = addOpen || editTarget !== null
  const isEditing = editTarget !== null

  const ProjectForm = (
    <Form
      form={form}
      layout="vertical"
      onFinish={values => isEditing ? editMutation.mutate(values) : addMutation.mutate(values)}
    >
      <Form.Item name="project_name" label={t('project.name')} rules={[{ required: true, message: t('project.nameRequired') }]}>
        <Input />
      </Form.Item>
      <Form.Item name="client_name" label={t('project.clientName')}>
        <Input />
      </Form.Item>
      <Form.Item name="industry" label={t('project.industry')}>
        <Input />
      </Form.Item>
      <Form.Item name="role" label={t('project.role')} rules={[{ required: true, message: t('project.roleRequired') }]}>
        <Select>
          {PROJECT_ROLES.map(r => (
            <Select.Option key={r} value={r}>{t(`projectRole.${r}`)}</Select.Option>
          ))}
        </Select>
      </Form.Item>
      <Form.Item name="started_at" label={t('project.startedAt')} rules={[{ required: true, message: t('project.startedAtRequired') }]}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item name="ended_at" label={t('project.endedAt')}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item name="tech_stack_input" label={t('project.techStack')} help={t('project.techStackPlaceholder')}>
        <Input />
      </Form.Item>
      <Form.Item name="team_size" label={t('project.teamSize')}>
        <InputNumber min={1} style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item name="responsibilities" label={t('project.responsibilities')}>
        <Input.TextArea rows={3} />
      </Form.Item>
      <Form.Item name="achievements" label={t('project.achievements')}>
        <Input.TextArea rows={3} />
      </Form.Item>
    </Form>
  )

  return (
    <div>
      {ctx}
      {canEdit && (
        <div style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddOpen(true)}>
            {t('project.add')}
          </Button>
        </div>
      )}

      {isLoading ? null : projects.length === 0 ? (
        <Typography.Text type="secondary">{t('project.noProjects')}</Typography.Text>
      ) : (
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {projects.map(proj => (
            <Card
              key={proj.id}
              size="small"
              title={
                <Space>
                  <Typography.Text strong>{proj.project.name}</Typography.Text>
                  <Tag>{t(`projectRole.${proj.role}`)}</Tag>
                  {!proj.ended_at && <Tag color="blue">{t('project.onGoing')}</Tag>}
                </Space>
              }
              extra={
                canEdit && (
                  <Space>
                    <Button
                      size="small"
                      icon={<EditOutlined />}
                      onClick={() => handleOpenEdit(proj)}
                    />
                    <Popconfirm
                      title={t('project.deleteConfirm')}
                      onConfirm={() => deleteMutation.mutate(proj.id)}
                      okText={t('action.confirm')}
                      cancelText={t('action.cancel')}
                    >
                      <Button size="small" danger icon={<DeleteOutlined />} />
                    </Popconfirm>
                  </Space>
                )
              }
            >
              {proj.project.client_name && (
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {proj.project.client_name}
                  {proj.project.industry && ` / ${proj.project.industry}`}
                </Typography.Text>
              )}
              <div style={{ marginTop: 4 }}>
                <Typography.Text style={{ fontSize: 12 }}>
                  {proj.started_at} ~ {proj.ended_at ?? t('project.onGoing')}
                </Typography.Text>
                {proj.team_size && (
                  <Typography.Text type="secondary" style={{ fontSize: 12, marginLeft: 12 }}>
                    {t('project.teamSize')}: {proj.team_size}
                  </Typography.Text>
                )}
              </div>
              {proj.tech_stack && proj.tech_stack.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  {proj.tech_stack.map(t => (
                    <Tag key={t} style={{ marginBottom: 4 }}>{t}</Tag>
                  ))}
                </div>
              )}
              {proj.responsibilities && (
                <Typography.Paragraph
                  style={{ marginTop: 8, marginBottom: 0, fontSize: 13 }}
                  ellipsis={{ rows: 2, expandable: true }}
                >
                  {proj.responsibilities}
                </Typography.Paragraph>
              )}
            </Card>
          ))}
        </Space>
      )}

      <Modal
        open={isModalOpen}
        title={isEditing ? t('project.editModal') : t('project.addModal')}
        onCancel={handleCloseModal}
        onOk={() => form.submit()}
        confirmLoading={addMutation.isPending || editMutation.isPending}
        okText={t('action.save')}
        cancelText={t('action.cancel')}
        width={600}
      >
        {ProjectForm}
      </Modal>
    </div>
  )
}
