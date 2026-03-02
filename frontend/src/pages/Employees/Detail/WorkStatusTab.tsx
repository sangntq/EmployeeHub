import { useState } from 'react'
import {
  Button,
  DatePicker,
  Descriptions,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from 'antd'
import { EditOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import dayjs from 'dayjs'
import { workStatusApi } from '../../../api/workStatus'

const STATUS_COLORS: Record<string, string> = {
  ASSIGNED: 'blue',
  FREE_IMMEDIATE: 'green',
  FREE_PLANNED: 'cyan',
  INTERNAL: 'purple',
  LEAVE: 'orange',
  LEAVING: 'red',
}

interface Props {
  employeeId: string
  canEdit: boolean  // manager以上
}

export default function WorkStatusTab({ employeeId, canEdit }: Props) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [messageApi, ctx] = message.useMessage()
  const [updateOpen, setUpdateOpen] = useState(false)
  const [form] = Form.useForm()

  const { data: ws } = useQuery({
    queryKey: ['work-status', employeeId],
    queryFn: () => workStatusApi.getWorkStatus(employeeId),
  })

  const { data: assignments = [], isLoading: assignLoading } = useQuery({
    queryKey: ['assignments', employeeId],
    queryFn: () => workStatusApi.listAssignments(employeeId),
  })

  const updateMutation = useMutation({
    mutationFn: (values: { status: string; free_from?: dayjs.Dayjs; note?: string }) => {
      return workStatusApi.updateWorkStatus(employeeId, {
        status: values.status,
        free_from: values.free_from ? values.free_from.format('YYYY-MM-DD') : null,
        note: values.note,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-status', employeeId] })
      setUpdateOpen(false)
      form.resetFields()
      messageApi.success(t('common.saved'))
    },
    onError: () => messageApi.error(t('common.error')),
  })

  const handleOpenUpdate = () => {
    if (ws) {
      form.setFieldsValue({
        status: ws.status,
        free_from: ws.free_from ? dayjs(ws.free_from) : undefined,
        note: ws.note,
      })
    }
    setUpdateOpen(true)
  }

  const assignmentColumns = [
    {
      title: t('workStatus.project'),
      dataIndex: 'project_name',
      key: 'project_name',
      render: (name: string | null) => name ?? '—',
    },
    {
      title: t('workStatus.allocationPercent'),
      dataIndex: 'allocation_percent',
      key: 'allocation_percent',
      render: (v: number) => `${v}%`,
    },
    {
      title: t('workStatus.startedAt'),
      dataIndex: 'started_at',
      key: 'started_at',
    },
    {
      title: t('workStatus.endsAt'),
      dataIndex: 'ends_at',
      key: 'ends_at',
      render: (v: string | null) => v ?? '—',
    },
    {
      title: t('common.status'),
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'default'}>
          {active ? t('workStatus.active') : t('workStatus.ended')}
        </Tag>
      ),
    },
  ]

  return (
    <div>
      {ctx}

      {/* 稼働状況 */}
      <Space style={{ marginBottom: 16 }} align="center">
        <Typography.Title level={5} style={{ margin: 0 }}>
          {t('workStatus.currentStatus')}
        </Typography.Title>
        {canEdit && (
          <Button size="small" icon={<EditOutlined />} onClick={handleOpenUpdate}>
            {t('workStatus.updateStatus')}
          </Button>
        )}
      </Space>

      <Descriptions bordered column={2} size="middle" style={{ marginBottom: 24 }}>
        <Descriptions.Item label={t('common.status')} span={1}>
          {ws ? (
            <Tag color={STATUS_COLORS[ws.status] ?? 'default'}>
              {t(`workStatus.${ws.status}`)}
            </Tag>
          ) : (
            <Tag color="green">{t('workStatus.FREE_IMMEDIATE')}</Tag>
          )}
        </Descriptions.Item>
        <Descriptions.Item label={t('workStatus.freeFrom')} span={1}>
          {ws?.free_from ?? '—'}
        </Descriptions.Item>
        <Descriptions.Item label={t('workStatus.note')} span={2}>
          {ws?.note ?? '—'}
        </Descriptions.Item>
      </Descriptions>

      {/* アサイン一覧 */}
      <Typography.Title level={5}>{t('workStatus.assignments')}</Typography.Title>
      <Table
        dataSource={assignments}
        columns={assignmentColumns}
        rowKey="id"
        loading={assignLoading}
        size="small"
        pagination={false}
        locale={{ emptyText: t('workStatus.noAssignments') }}
      />

      {/* 稼働状況更新モーダル */}
      <Modal
        open={updateOpen}
        title={t('workStatus.updateStatus')}
        onCancel={() => { setUpdateOpen(false); form.resetFields() }}
        onOk={() => form.submit()}
        confirmLoading={updateMutation.isPending}
        okText={t('action.save')}
        cancelText={t('action.cancel')}
      >
        <Form form={form} layout="vertical" onFinish={values => updateMutation.mutate(values)}>
          <Form.Item name="status" label={t('common.status')} rules={[{ required: true }]}>
            <Select>
              {['ASSIGNED', 'FREE_IMMEDIATE', 'FREE_PLANNED', 'INTERNAL', 'LEAVE', 'LEAVING'].map(s => (
                <Select.Option key={s} value={s}>
                  <Tag color={STATUS_COLORS[s]}>{t(`workStatus.${s}`)}</Tag>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            noStyle
            shouldUpdate={(prev, curr) => prev.status !== curr.status}
          >
            {({ getFieldValue }) =>
              getFieldValue('status') === 'FREE_PLANNED' ? (
                <Form.Item name="free_from" label={t('workStatus.freeFrom')}>
                  <DatePicker style={{ width: '100%' }} />
                </Form.Item>
              ) : null
            }
          </Form.Item>
          <Form.Item name="note" label={t('workStatus.note')}>
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
