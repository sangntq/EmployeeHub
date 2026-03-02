import { useState } from 'react'
import {
  Alert,
  Button,
  DatePicker,
  Descriptions,
  Form,
  Input,
  Modal,
  message,
} from 'antd'
import { EditOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import dayjs from 'dayjs'
import { projectsApi } from '../../../api/projects'
import type { VisaUpdateData } from '../../../api/projects'

interface Props {
  employeeId: string
  canView: boolean    // 本人 / department_head / admin
  canEdit: boolean    // department_head / admin
}

export default function VisaTab({ employeeId, canView, canEdit }: Props) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [messageApi, ctx] = message.useMessage()
  const [editOpen, setEditOpen] = useState(false)
  const [form] = Form.useForm()

  const { data: visa } = useQuery({
    queryKey: ['visa', employeeId],
    queryFn: () => projectsApi.getVisa(employeeId),
    enabled: canView,
  })

  const updateMutation = useMutation({
    mutationFn: (values: { visa_type?: string; residence_card_number?: string; expires_at?: dayjs.Dayjs; notes?: string }) => {
      const data: VisaUpdateData = {
        visa_type: values.visa_type,
        residence_card_number: values.residence_card_number,
        expires_at: values.expires_at ? values.expires_at.format('YYYY-MM-DD') : null,
        notes: values.notes,
      }
      return projectsApi.updateVisa(employeeId, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visa', employeeId] })
      setEditOpen(false)
      form.resetFields()
      messageApi.success(t('common.saved'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  if (!canView) {
    return <Alert type="warning" message={t('visa.restricted')} showIcon />
  }

  const handleOpenEdit = () => {
    if (visa) {
      form.setFieldsValue({
        visa_type: visa.visa_type,
        residence_card_number: visa.residence_card_number,
        expires_at: visa.expires_at ? dayjs(visa.expires_at) : undefined,
        notes: visa.notes,
      })
    }
    setEditOpen(true)
  }

  return (
    <div>
      {ctx}

      {canEdit && (
        <div style={{ marginBottom: 16 }}>
          <Button icon={<EditOutlined />} onClick={handleOpenEdit}>
            {t('visa.update')}
          </Button>
        </div>
      )}

      {!visa ? (
        <Alert type="info" message={t('visa.noData')} showIcon />
      ) : (
        <Descriptions bordered column={2} size="middle">
          <Descriptions.Item label={t('visa.type')} span={2}>
            {visa.visa_type ?? '—'}
          </Descriptions.Item>
          <Descriptions.Item label={t('visa.residenceCard')}>
            {visa.residence_card_number ?? '—'}
          </Descriptions.Item>
          <Descriptions.Item label={t('visa.expiresAt')}>
            {visa.expires_at ?? '—'}
          </Descriptions.Item>
          <Descriptions.Item label={t('visa.notes')} span={2}>
            {visa.notes ?? '—'}
          </Descriptions.Item>
        </Descriptions>
      )}

      <Modal
        open={editOpen}
        title={t('visa.update')}
        onCancel={() => { setEditOpen(false); form.resetFields() }}
        onOk={() => form.submit()}
        confirmLoading={updateMutation.isPending}
        okText={t('action.save')}
        cancelText={t('action.cancel')}
      >
        <Form form={form} layout="vertical" onFinish={values => updateMutation.mutate(values)}>
          <Form.Item name="visa_type" label={t('visa.type')}>
            <Input />
          </Form.Item>
          <Form.Item name="residence_card_number" label={t('visa.residenceCard')}>
            <Input />
          </Form.Item>
          <Form.Item name="expires_at" label={t('visa.expiresAt')}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="notes" label={t('visa.notes')}>
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
