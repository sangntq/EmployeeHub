import { useState } from 'react'
import {
  Button,
  Form,
  Input,
  InputNumber,
  Modal,
  Rate,
  Select,
  Space,
  Table,
  Tag,
  Tooltip,
  Typography,
  message,
} from 'antd'
import { PlusOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { skillsApi } from '../../../api/skills'
import type { EmployeeSkill, SkillItem } from '../../../api/skills'

const { Option, OptGroup } = Select

const LEVEL_COLORS: Record<number, string> = {
  1: 'default',
  2: 'blue',
  3: 'cyan',
  4: 'green',
  5: 'gold',
}

function LevelTag({ level, label }: { level: number; label: string }) {
  return <Tag color={LEVEL_COLORS[level] ?? 'default'}>{label}</Tag>
}

function StatusTag({ status }: { status: string }) {
  const colorMap: Record<string, string> = {
    PENDING: 'orange',
    APPROVED: 'green',
    REJECTED: 'red',
  }
  const { t } = useTranslation()
  return <Tag color={colorMap[status] ?? 'default'}>{t(`approval.${status}`)}</Tag>
}

interface Props {
  employeeId: string
  canApply: boolean   // 本人
  canApprove: boolean // manager以上
}

export default function SkillsTab({ employeeId, canApply, canApprove }: Props) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [messageApi, ctx] = message.useMessage()

  const [applyOpen, setApplyOpen] = useState(false)
  const [approveOpen, setApproveOpen] = useState<EmployeeSkill | null>(null)
  const [rejectOpen, setRejectOpen] = useState<EmployeeSkill | null>(null)
  const [applyForm] = Form.useForm()
  const [approveForm] = Form.useForm()
  const [rejectForm] = Form.useForm()

  const { data: masters } = useQuery({
    queryKey: ['skill-masters'],
    queryFn: skillsApi.listMasters,
  })

  const { data: skills = [], isLoading } = useQuery({
    queryKey: ['employee-skills', employeeId],
    queryFn: () => skillsApi.listEmployeeSkills(employeeId),
  })

  const applyMutation = useMutation({
    mutationFn: (values: Parameters<typeof skillsApi.apply>[1]) =>
      skillsApi.apply(employeeId, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-skills', employeeId] })
      setApplyOpen(false)
      applyForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      const detail = err?.response?.data?.detail ?? t('common.error')
      messageApi.error(detail)
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof skillsApi.approve>[1] }) =>
      skillsApi.approve(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-skills', employeeId] })
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      setApproveOpen(null)
      approveForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof skillsApi.reject>[1] }) =>
      skillsApi.reject(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-skills', employeeId] })
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      setRejectOpen(null)
      rejectForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const levelLabel = (level: number) => t(`skillLevel.level${level}`)

  const columns = [
    {
      title: t('common.name'),
      dataIndex: ['skill', 'name'],
      key: 'skill_name',
    },
    {
      title: t('skill.selfLevelCol'),
      key: 'self_level',
      render: (_: unknown, r: EmployeeSkill) => (
        <LevelTag level={r.self_level} label={`Lv${r.self_level} ${levelLabel(r.self_level)}`} />
      ),
    },
    {
      title: t('skill.approvedLevelCol'),
      key: 'approved_level',
      render: (_: unknown, r: EmployeeSkill) =>
        r.approved_level != null ? (
          <LevelTag level={r.approved_level} label={`Lv${r.approved_level} ${levelLabel(r.approved_level)}`} />
        ) : (
          <Typography.Text type="secondary">—</Typography.Text>
        ),
    },
    {
      title: t('skill.experienceYears'),
      key: 'experience_years',
      render: (_: unknown, r: EmployeeSkill) =>
        r.experience_years != null
          ? `${r.experience_years} ${t('skill.experienceYearsAddon')}`
          : '—',
    },
    {
      title: t('common.status'),
      key: 'status',
      render: (_: unknown, r: EmployeeSkill) => <StatusTag status={r.status} />,
    },
    ...(canApprove
      ? [
          {
            title: t('action.approve') + ' / ' + t('action.reject'),
            key: 'actions',
            render: (_: unknown, r: EmployeeSkill) =>
              r.status === 'PENDING' ? (
                <Space>
                  <Tooltip title={t('action.approve')}>
                    <Button
                      size="small"
                      type="primary"
                      icon={<CheckOutlined />}
                      onClick={() => setApproveOpen(r)}
                    />
                  </Tooltip>
                  <Tooltip title={t('action.reject')}>
                    <Button
                      size="small"
                      danger
                      icon={<CloseOutlined />}
                      onClick={() => setRejectOpen(r)}
                    />
                  </Tooltip>
                </Space>
              ) : null,
          },
        ]
      : []),
  ]

  return (
    <div>
      {ctx}
      {canApply && (
        <div style={{ marginBottom: 12 }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setApplyOpen(true)}
          >
            {t('skill.submitSkill')}
          </Button>
        </div>
      )}

      <Table
        dataSource={skills}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={false}
        size="small"
      />

      {/* スキル申請モーダル */}
      <Modal
        title={t('skill.applyModal')}
        open={applyOpen}
        onCancel={() => { setApplyOpen(false); applyForm.resetFields() }}
        onOk={() => applyForm.submit()}
        confirmLoading={applyMutation.isPending}
        okText={t('action.submit')}
      >
        <Form
          form={applyForm}
          layout="vertical"
          onFinish={values => applyMutation.mutate(values)}
        >
          <Form.Item
            name="skill_id"
            label={t('skill.selectSkill')}
            rules={[{ required: true, message: t('skill.selectSkillRequired') }]}
          >
            <Select
              showSearch
              placeholder={t('skill.selectSkillPlaceholder')}
              optionFilterProp="label"
              filterOption={(input, opt) =>
                (opt?.label?.toString() ?? '').toLowerCase().includes(input.toLowerCase())
              }
            >
              {masters?.categories.map(cat => (
                <OptGroup key={cat.id} label={cat.name_ja}>
                  {cat.skills
                    .filter(s => !skills.some(es => es.skill.id === s.id))
                    .map((s: SkillItem) => (
                      <Option key={s.id} value={s.id} label={s.name}>
                        {s.name}
                      </Option>
                    ))}
                </OptGroup>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="self_level"
            label={t('skill.selfLevelForm')}
            rules={[{ required: true, message: t('skill.selfLevelRequired') }]}
          >
            <Rate count={5} />
          </Form.Item>

          <Form.Item name="experience_years" label={t('skill.experienceYears')}>
            <InputNumber
              min={0}
              max={50}
              step={0.5}
              addonAfter={t('skill.experienceYearsAddon')}
              style={{ width: 140 }}
            />
          </Form.Item>

          <Form.Item name="self_comment" label={t('skill.commentField')}>
            <Input.TextArea placeholder={t('skill.commentPlaceholder')} rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      {/* スキル承認モーダル */}
      <Modal
        title={t('skill.approveModal', { name: approveOpen?.skill.name })}
        open={!!approveOpen}
        onCancel={() => { setApproveOpen(null); approveForm.resetFields() }}
        onOk={() => approveForm.submit()}
        confirmLoading={approveMutation.isPending}
        okText={t('action.approve')}
      >
        <Form
          form={approveForm}
          layout="vertical"
          onFinish={values =>
            approveMutation.mutate({ id: approveOpen!.id, data: values })
          }
        >
          <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            {approveOpen
              ? t('skill.selfLevelInfo', {
                  level: approveOpen.self_level,
                  label: levelLabel(approveOpen.self_level),
                })
              : ''}
          </Typography.Text>
          <Form.Item
            name="approved_level"
            label={t('skill.approvedLevelForm')}
            rules={[{ required: true, message: t('skill.approvedLevelRequired') }]}
          >
            <Rate count={5} />
          </Form.Item>
          <Form.Item name="approver_comment" label={t('skill.approverComment')}>
            <Input placeholder={t('skill.approverCommentPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>

      {/* スキル差し戻しモーダル */}
      <Modal
        title={t('skill.rejectModal', { name: rejectOpen?.skill.name })}
        open={!!rejectOpen}
        onCancel={() => { setRejectOpen(null); rejectForm.resetFields() }}
        onOk={() => rejectForm.submit()}
        confirmLoading={rejectMutation.isPending}
        okText={t('action.reject')}
        okButtonProps={{ danger: true }}
      >
        <Form
          form={rejectForm}
          layout="vertical"
          onFinish={values =>
            rejectMutation.mutate({ id: rejectOpen!.id, data: values })
          }
        >
          <Form.Item
            name="approver_comment"
            label={t('skill.rejectReason')}
            rules={[{ required: true, message: t('skill.rejectReasonRequired') }]}
          >
            <Input placeholder={t('skill.rejectReasonPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
