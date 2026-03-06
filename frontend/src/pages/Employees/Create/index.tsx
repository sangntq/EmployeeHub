import {
  Button,
  Card,
  Col,
  DatePicker,
  Form,
  Input,
  Row,
  Select,
  Space,
  message,
} from 'antd'
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { AxiosError } from 'axios'
import { employeesApi } from '../../../api/employees'
import type { EmployeeCreateData } from '../../../api/employees'
import PageHeader from '../../../components/common/PageHeader'
import dayjs from 'dayjs'

const { Option } = Select

const OFFICE_OPTIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const WORK_STYLE_OPTIONS = ['ONSITE', 'REMOTE', 'HYBRID']
const EMPLOYMENT_TYPE_OPTIONS = ['FULLTIME', 'CONTRACT', 'FREELANCE']
const ROLE_OPTIONS = ['member', 'manager', 'department_head', 'sales', 'director', 'admin']
const JAPANESE_LEVEL_OPTIONS = ['NONE', 'N5', 'N4', 'N3', 'N2', 'N1', 'NATIVE']

export default function EmployeeCreatePage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [messageApi, ctx] = message.useMessage()

  const createMutation = useMutation({
    mutationFn: (data: EmployeeCreateData) => employeesApi.create(data),
    onSuccess: (result) => {
      messageApi.success(t('common.saved'))
      navigate(`/employees/${result.id}`)
    },
    onError: (error: unknown) => {
      const axiosErr = error as AxiosError<{ detail?: string }>
      const detail = axiosErr.response?.data?.detail
      const httpStatus = axiosErr.response?.status

      // 社員番号の重複（409 Conflict）
      if (httpStatus === 409 && detail) {
        form.setFields([{ name: 'employee_number', errors: [detail] }])
        form.scrollToField('employee_number')
        messageApi.error(detail)
        return
      }

      // バックエンドからの具体的なエラーメッセージ
      if (detail) {
        messageApi.error(detail)
        return
      }

      messageApi.error(t('common.error'))
    },
  })

  const handleSubmit = () => {
    form.validateFields().then(values => {
      const data: EmployeeCreateData = {
        ...values,
        joined_at: values.joined_at ? dayjs(values.joined_at).format('YYYY-MM-DD') : undefined,
      }
      createMutation.mutate(data)
    })
  }

  return (
    <div>
      {ctx}
      <PageHeader
        title={t('action.add')}
        breadcrumbs={[
          { title: t('page.employees'), href: '/employees' },
          { title: t('action.add') },
        ]}
      />

      <Card>
        <Form form={form} layout="vertical" initialValues={{ system_role: 'member', office_location: 'HANOI', employment_type: 'FULLTIME', work_style: 'ONSITE' }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="employee_number" label={t('common.employeeNumber')} rules={[{ required: true, message: `${t('common.employeeNumber')} ${t('common.required')}` }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="email" label={t('auth.email')} rules={[{ required: true, message: `${t('auth.email')} ${t('common.required')}` }, { type: 'email', message: `${t('auth.email')} が正しくありません` }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="name_ja" label={t('profile.nameJa')} rules={[{ required: true, message: `${t('profile.nameJa')} ${t('common.required')}` }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="name_en" label={t('profile.nameEn')}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="name_vi" label={t('profile.nameVi')}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="office_location" label={t('common.officeLocation')} rules={[{ required: true, message: `${t('common.officeLocation')} ${t('common.required')}` }]}>
                <Select>
                  {OFFICE_OPTIONS.map(o => (
                    <Option key={o} value={o}>{t(`officeLocation.${o}`)}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="work_style" label={t('common.workStyle')}>
                <Select>
                  {WORK_STYLE_OPTIONS.map(o => (
                    <Option key={o} value={o}>{t(`workStyle.${o}`)}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="employment_type" label={t('common.employmentType')}>
                <Select>
                  {EMPLOYMENT_TYPE_OPTIONS.map(o => (
                    <Option key={o} value={o}>{t(`employmentType.${o}`)}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="system_role" label={t('common.role')}>
                <Select>
                  {ROLE_OPTIONS.map(r => (
                    <Option key={r} value={r}>{t(`role.${r}`)}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="joined_at" label={t('common.joinedAt')} rules={[{ required: true, message: `${t('common.joinedAt')} ${t('common.required')}` }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="japanese_level" label={t('employee.japaneseLevel')}>
                <Select allowClear>
                  {JAPANESE_LEVEL_OPTIONS.map(l => (
                    <Option key={l} value={l}>{t(`japaneseLevel.${l}`)}</Option>
                  ))}
                </Select>
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
          </Row>
        </Form>
      </Card>

      <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/employees')}>
          {t('action.back')}
        </Button>
        <Space>
          <Button onClick={() => navigate('/employees')}>{t('action.cancel')}</Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            loading={createMutation.isPending}
            onClick={handleSubmit}
          >
            {t('action.save')}
          </Button>
        </Space>
      </div>
    </div>
  )
}
