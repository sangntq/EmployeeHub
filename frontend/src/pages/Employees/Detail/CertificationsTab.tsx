import { useState } from 'react'
import {
  Button,
  DatePicker,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Tooltip,
  message,
} from 'antd'
import { PlusOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import dayjs from 'dayjs'
import { certificationsApi } from '../../../api/certifications'
import type { EmployeeCertification } from '../../../api/certifications'

const { Option } = Select

function StatusTag({ status }: { status: string }) {
  const colorMap: Record<string, string> = { PENDING: 'orange', APPROVED: 'green', REJECTED: 'red' }
  const { t } = useTranslation()
  return <Tag color={colorMap[status] ?? 'default'}>{t(`approval.${status}`)}</Tag>
}

interface Props {
  employeeId: string
  canApply: boolean
  canApprove: boolean
}

export default function CertificationsTab({ employeeId, canApply, canApprove }: Props) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [messageApi, ctx] = message.useMessage()

  const [applyOpen, setApplyOpen] = useState(false)
  const [approveOpen, setApproveOpen] = useState<EmployeeCertification | null>(null)
  const [rejectOpen, setRejectOpen] = useState<EmployeeCertification | null>(null)
  const [useCustomName, setUseCustomName] = useState(false)
  const [applyForm] = Form.useForm()
  const [approveForm] = Form.useForm()
  const [rejectForm] = Form.useForm()

  const { data: masters = [] } = useQuery({
    queryKey: ['cert-masters'],
    queryFn: certificationsApi.listMasters,
  })

  const { data: certs = [], isLoading } = useQuery({
    queryKey: ['employee-certs', employeeId],
    queryFn: () => certificationsApi.listEmployeeCerts(employeeId),
  })

  const applyMutation = useMutation({
    mutationFn: (values: Parameters<typeof certificationsApi.apply>[1]) =>
      certificationsApi.apply(employeeId, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-certs', employeeId] })
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
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof certificationsApi.approve>[1] }) =>
      certificationsApi.approve(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-certs', employeeId] })
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      setApproveOpen(null)
      approveForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof certificationsApi.reject>[1] }) =>
      certificationsApi.reject(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-certs', employeeId] })
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      setRejectOpen(null)
      rejectForm.resetFields()
      messageApi.success(t('common.success'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const certName = (c: EmployeeCertification) =>
    c.certification_master?.name ?? c.custom_name ?? '—'

  const handleApplyFinish = (values: {
    obtained_at: dayjs.Dayjs
    expires_at?: dayjs.Dayjs
    score?: string
    custom_name?: string
    certification_master_id?: string
  }) => {
    const payload: Parameters<typeof certificationsApi.apply>[1] = {
      obtained_at: dayjs(values.obtained_at).format('YYYY-MM-DD'),
      score: values.score || undefined,
      expires_at: values.expires_at ? dayjs(values.expires_at).format('YYYY-MM-DD') : undefined,
    }
    if (useCustomName) {
      payload.custom_name = values.custom_name
    } else {
      payload.certification_master_id = values.certification_master_id
    }
    applyMutation.mutate(payload)
  }

  const columns = [
    {
      title: t('cert.certNameCol'),
      key: 'name',
      render: (_: unknown, r: EmployeeCertification) => certName(r),
    },
    {
      title: t('cert.categoryCol'),
      key: 'category',
      render: (_: unknown, r: EmployeeCertification) =>
        r.certification_master
          ? (t(`certCategory.${r.certification_master.category}`, { defaultValue: r.certification_master.category }))
          : <Tag>{t('cert.custom')}</Tag>,
    },
    {
      title: t('cert.obtainedAt'),
      dataIndex: 'obtained_at',
      key: 'obtained_at',
    },
    {
      title: t('approval.expiresAtCol'),
      key: 'expires_at',
      render: (_: unknown, r: EmployeeCertification) => r.expires_at ?? '—',
    },
    {
      title: t('approval.scoreCol'),
      key: 'score',
      render: (_: unknown, r: EmployeeCertification) => r.score ?? '—',
    },
    {
      title: t('common.status'),
      key: 'status',
      render: (_: unknown, r: EmployeeCertification) => <StatusTag status={r.status} />,
    },
    ...(canApprove
      ? [
          {
            title: t('action.approve') + ' / ' + t('action.reject'),
            key: 'actions',
            render: (_: unknown, r: EmployeeCertification) =>
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
            {t('cert.submitCert')}
          </Button>
        </div>
      )}

      <Table
        dataSource={certs}
        columns={columns}
        rowKey="id"
        loading={isLoading}
        pagination={false}
        size="small"
      />

      {/* 資格申請モーダル */}
      <Modal
        title={t('cert.applyModal')}
        open={applyOpen}
        onCancel={() => { setApplyOpen(false); applyForm.resetFields(); setUseCustomName(false) }}
        onOk={() => applyForm.submit()}
        confirmLoading={applyMutation.isPending}
        okText={t('action.submit')}
      >
        <Form form={applyForm} layout="vertical" onFinish={handleApplyFinish}>
          <Form.Item label={t('cert.category')}>
            <Select
              value={useCustomName ? 'custom' : 'master'}
              onChange={v => {
                setUseCustomName(v === 'custom')
                applyForm.resetFields(['certification_master_id', 'custom_name'])
              }}
            >
              <Option value="master">{t('cert.selectFromMaster')}</Option>
              <Option value="custom">{t('cert.customName')}</Option>
            </Select>
          </Form.Item>

          {useCustomName ? (
            <Form.Item
              name="custom_name"
              label={t('cert.certNameField')}
              rules={[{ required: true, message: t('cert.certNameRequired') }]}
            >
              <Input placeholder={t('cert.certNamePlaceholder')} />
            </Form.Item>
          ) : (
            <Form.Item
              name="certification_master_id"
              label={t('cert.selectCert')}
              rules={[{ required: true, message: t('cert.selectCertRequired') }]}
            >
              <Select
                showSearch
                placeholder={t('cert.selectCertPlaceholder')}
                optionFilterProp="children"
                filterOption={(input, opt) =>
                  (opt?.children?.toString() ?? '').toLowerCase().includes(input.toLowerCase())
                }
              >
                {Object.entries(
                  masters.reduce<Record<string, typeof masters>>((acc, m) => {
                    const cat = t(`certCategory.${m.category}`, { defaultValue: m.category })
                    if (!acc[cat]) acc[cat] = []
                    acc[cat].push(m)
                    return acc
                  }, {})
                ).map(([cat, items]) => (
                  <Select.OptGroup key={cat} label={cat}>
                    {(items as typeof masters).map(m => (
                      <Option key={m.id} value={m.id}>{m.name}</Option>
                    ))}
                  </Select.OptGroup>
                ))}
              </Select>
            </Form.Item>
          )}

          <Form.Item
            name="obtained_at"
            label={t('cert.obtainedAt')}
            rules={[{ required: true, message: t('cert.obtainedAtRequired') }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="expires_at" label={t('cert.expiresAt')}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="score" label={t('cert.score')}>
            <Input placeholder={t('cert.scorePlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 資格承認モーダル */}
      <Modal
        title={t('cert.approveModal', { name: approveOpen ? certName(approveOpen) : '' })}
        open={!!approveOpen}
        onCancel={() => { setApproveOpen(null); approveForm.resetFields() }}
        onOk={() => approveForm.submit()}
        confirmLoading={approveMutation.isPending}
        okText={t('action.approve')}
      >
        <Form
          form={approveForm}
          layout="vertical"
          onFinish={values => approveMutation.mutate({ id: approveOpen!.id, data: values })}
        >
          <Form.Item name="approver_comment" label={t('cert.approverComment')}>
            <Input placeholder={t('cert.approverCommentPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 資格差し戻しモーダル */}
      <Modal
        title={t('cert.rejectModal', { name: rejectOpen ? certName(rejectOpen) : '' })}
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
          onFinish={values => rejectMutation.mutate({ id: rejectOpen!.id, data: values })}
        >
          <Form.Item
            name="approver_comment"
            label={t('cert.rejectReason')}
            rules={[{ required: true, message: t('cert.rejectReasonRequired') }]}
          >
            <Input placeholder={t('cert.rejectReasonPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
