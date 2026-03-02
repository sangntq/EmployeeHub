import {
  Button,
  Card,
  Col,
  Form,
  Input,
  Modal,
  Rate,
  Row,
  Space,
  Table,
  Tag,
  Tooltip,
  Typography,
  message,
} from 'antd'
import { CheckOutlined, CloseOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import { certificationsApi } from '../../api/certifications'
import type { PendingCertItem } from '../../api/certifications'
import { skillsApi } from '../../api/skills'
import type { PendingSkillItem } from '../../api/skills'
import PageHeader from '../../components/common/PageHeader'

export default function ApprovalQueuePage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [messageApi, ctx] = message.useMessage()

  const [approveSkillOpen, setApproveSkillOpen] = useState<PendingSkillItem | null>(null)
  const [rejectSkillOpen, setRejectSkillOpen] = useState<PendingSkillItem | null>(null)
  const [approveCertOpen, setApproveCertOpen] = useState<PendingCertItem | null>(null)
  const [rejectCertOpen, setRejectCertOpen] = useState<PendingCertItem | null>(null)
  const [approveSkillForm] = Form.useForm()
  const [rejectSkillForm] = Form.useForm()
  const [approveCertForm] = Form.useForm()
  const [rejectCertForm] = Form.useForm()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: certificationsApi.listPendingApprovals,
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
  }

  const approveSkillMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof skillsApi.approve>[1] }) =>
      skillsApi.approve(id, data),
    onSuccess: () => {
      invalidate()
      setApproveSkillOpen(null)
      approveSkillForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const rejectSkillMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof skillsApi.reject>[1] }) =>
      skillsApi.reject(id, data),
    onSuccess: () => {
      invalidate()
      setRejectSkillOpen(null)
      rejectSkillForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const approveCertMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof certificationsApi.approve>[1] }) =>
      certificationsApi.approve(id, data),
    onSuccess: () => {
      invalidate()
      setApproveCertOpen(null)
      approveCertForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const rejectCertMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof certificationsApi.reject>[1] }) =>
      certificationsApi.reject(id, data),
    onSuccess: () => {
      invalidate()
      setRejectCertOpen(null)
      rejectCertForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const levelLabel = (level: number) => t(`skillLevel.level${level}`)

  const pendingSkills = data?.skills ?? []
  const pendingCerts = data?.certifications ?? []

  const skillColumns = [
    {
      title: t('common.employeeNumber'),
      dataIndex: 'employee_number',
      key: 'employee_number',
      width: 110,
    },
    {
      title: t('approval.employeeNameCol'),
      dataIndex: 'employee_name_ja',
      key: 'employee_name_ja',
    },
    {
      title: t('approval.skillCol'),
      dataIndex: 'skill_name',
      key: 'skill_name',
    },
    {
      title: t('approval.selfLevelCol'),
      key: 'self_level',
      render: (_: unknown, r: PendingSkillItem) => (
        <Tag>{`Lv${r.self_level} ${levelLabel(r.self_level)}`}</Tag>
      ),
    },
    {
      title: t('approval.experienceYearsCol'),
      key: 'experience_years',
      render: (_: unknown, r: PendingSkillItem) =>
        r.experience_years != null
          ? `${r.experience_years} ${t('skill.experienceYearsAddon')}`
          : '—',
    },
    {
      title: t('approval.commentCol'),
      key: 'self_comment',
      render: (_: unknown, r: PendingSkillItem) => (
        <Typography.Text type="secondary">{r.self_comment ?? '—'}</Typography.Text>
      ),
    },
    {
      title: t('approval.submittedAtCol'),
      key: 'submitted_at',
      render: (_: unknown, r: PendingSkillItem) =>
        new Date(r.submitted_at).toLocaleDateString(),
    },
    {
      title: t('approval.actionsCol'),
      key: 'actions',
      render: (_: unknown, r: PendingSkillItem) => (
        <Space>
          <Tooltip title={t('action.approve')}>
            <Button
              size="small"
              type="primary"
              icon={<CheckOutlined />}
              onClick={() => setApproveSkillOpen(r)}
            />
          </Tooltip>
          <Tooltip title={t('action.reject')}>
            <Button
              size="small"
              danger
              icon={<CloseOutlined />}
              onClick={() => setRejectSkillOpen(r)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ]

  const certColumns = [
    {
      title: t('common.employeeNumber'),
      dataIndex: 'employee_number',
      key: 'employee_number',
      width: 110,
    },
    {
      title: t('approval.employeeNameCol'),
      dataIndex: 'employee_name_ja',
      key: 'employee_name_ja',
    },
    {
      title: t('approval.certNameCol'),
      dataIndex: 'cert_name',
      key: 'cert_name',
    },
    {
      title: t('approval.obtainedAtCol'),
      dataIndex: 'obtained_at',
      key: 'obtained_at',
    },
    {
      title: t('approval.expiresAtCol'),
      key: 'expires_at',
      render: (_: unknown, r: PendingCertItem) => r.expires_at ?? '—',
    },
    {
      title: t('approval.scoreCol'),
      key: 'score',
      render: (_: unknown, r: PendingCertItem) => r.score ?? '—',
    },
    {
      title: t('approval.submittedAtCol'),
      key: 'submitted_at',
      render: (_: unknown, r: PendingCertItem) =>
        new Date(r.submitted_at).toLocaleDateString(),
    },
    {
      title: t('approval.actionsCol'),
      key: 'actions',
      render: (_: unknown, r: PendingCertItem) => (
        <Space>
          <Tooltip title={t('action.approve')}>
            <Button
              size="small"
              type="primary"
              icon={<CheckOutlined />}
              onClick={() => setApproveCertOpen(r)}
            />
          </Tooltip>
          <Tooltip title={t('action.reject')}>
            <Button
              size="small"
              danger
              icon={<CloseOutlined />}
              onClick={() => setRejectCertOpen(r)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ]

  const totalPending = pendingSkills.length + pendingCerts.length

  return (
    <div>
      {ctx}
      <PageHeader
        title={t('page.approvalQueue')}
        breadcrumbs={[{ title: t('page.approvalQueue') }]}
        extra={
          <Button onClick={() => refetch()}>{t('action.refresh')}</Button>
        }
      />

      {totalPending === 0 && !isLoading && (
        <Card style={{ textAlign: 'center', padding: 40 }}>
          <Typography.Text type="secondary">{t('approval.noPending')}</Typography.Text>
        </Card>
      )}

      <Row gutter={[0, 16]}>
        {/* スキル承認待ち */}
        <Col span={24}>
          <Card
            title={
              <Space>
                {t('approval.skillSubmission')}
                {pendingSkills.length > 0 && (
                  <Tag color="orange">{t('approval.pendingCount', { count: pendingSkills.length })}</Tag>
                )}
              </Space>
            }
          >
            <Table
              dataSource={pendingSkills}
              columns={skillColumns}
              rowKey="id"
              loading={isLoading}
              pagination={false}
              size="small"
              locale={{ emptyText: t('approval.noSkillsPending') }}
            />
          </Card>
        </Col>

        {/* 資格承認待ち */}
        <Col span={24}>
          <Card
            title={
              <Space>
                {t('approval.certSubmission')}
                {pendingCerts.length > 0 && (
                  <Tag color="orange">{t('approval.pendingCount', { count: pendingCerts.length })}</Tag>
                )}
              </Space>
            }
          >
            <Table
              dataSource={pendingCerts}
              columns={certColumns}
              rowKey="id"
              loading={isLoading}
              pagination={false}
              size="small"
              locale={{ emptyText: t('approval.noCertsPending') }}
            />
          </Card>
        </Col>
      </Row>

      {/* スキル承認モーダル */}
      <Modal
        title={t('approval.approveSkillTitle', { name: approveSkillOpen?.skill_name })}
        open={!!approveSkillOpen}
        onCancel={() => { setApproveSkillOpen(null); approveSkillForm.resetFields() }}
        onOk={() => approveSkillForm.submit()}
        confirmLoading={approveSkillMutation.isPending}
        okText={t('action.approve')}
      >
        <Form
          form={approveSkillForm}
          layout="vertical"
          onFinish={values =>
            approveSkillMutation.mutate({ id: approveSkillOpen!.id, data: values })
          }
        >
          <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            {approveSkillOpen
              ? t('approval.selfLevelInfo', {
                  level: approveSkillOpen.self_level,
                  label: levelLabel(approveSkillOpen.self_level),
                })
              : ''}
          </Typography.Text>
          <Form.Item
            name="approved_level"
            label={t('approval.approvedLevelForm')}
            rules={[{ required: true, message: t('approval.approvedLevelRequired') }]}
          >
            <Rate count={5} />
          </Form.Item>
          <Form.Item name="approver_comment" label={t('approval.approverComment')}>
            <Input placeholder={t('approval.approverCommentPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>

      {/* スキル差し戻しモーダル */}
      <Modal
        title={t('approval.rejectSkillTitle', { name: rejectSkillOpen?.skill_name })}
        open={!!rejectSkillOpen}
        onCancel={() => { setRejectSkillOpen(null); rejectSkillForm.resetFields() }}
        onOk={() => rejectSkillForm.submit()}
        confirmLoading={rejectSkillMutation.isPending}
        okText={t('action.reject')}
        okButtonProps={{ danger: true }}
      >
        <Form
          form={rejectSkillForm}
          layout="vertical"
          onFinish={values =>
            rejectSkillMutation.mutate({ id: rejectSkillOpen!.id, data: values })
          }
        >
          <Form.Item
            name="approver_comment"
            label={t('approval.rejectReason')}
            rules={[{ required: true, message: t('approval.rejectReasonRequired') }]}
          >
            <Input placeholder={t('approval.rejectReasonPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 資格承認モーダル */}
      <Modal
        title={t('approval.approveCertTitle', { name: approveCertOpen?.cert_name })}
        open={!!approveCertOpen}
        onCancel={() => { setApproveCertOpen(null); approveCertForm.resetFields() }}
        onOk={() => approveCertForm.submit()}
        confirmLoading={approveCertMutation.isPending}
        okText={t('action.approve')}
      >
        <Form
          form={approveCertForm}
          layout="vertical"
          onFinish={values =>
            approveCertMutation.mutate({ id: approveCertOpen!.id, data: values })
          }
        >
          <Form.Item name="approver_comment" label={t('approval.approverComment')}>
            <Input placeholder={t('approval.approverCommentPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 資格差し戻しモーダル */}
      <Modal
        title={t('approval.rejectCertTitle', { name: rejectCertOpen?.cert_name })}
        open={!!rejectCertOpen}
        onCancel={() => { setRejectCertOpen(null); rejectCertForm.resetFields() }}
        onOk={() => rejectCertForm.submit()}
        confirmLoading={rejectCertMutation.isPending}
        okText={t('action.reject')}
        okButtonProps={{ danger: true }}
      >
        <Form
          form={rejectCertForm}
          layout="vertical"
          onFinish={values =>
            rejectCertMutation.mutate({ id: rejectCertOpen!.id, data: values })
          }
        >
          <Form.Item
            name="approver_comment"
            label={t('approval.rejectReason')}
            rules={[{ required: true, message: t('approval.rejectReasonRequired') }]}
          >
            <Input placeholder={t('approval.rejectReasonPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
