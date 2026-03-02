import { useState } from 'react'
import { Form, Input, Button, Divider, Card, Typography, Space, message } from 'antd'
import { GoogleOutlined, MailOutlined, LockOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'
import { authApi } from '../../api/auth'
import LanguageSwitcher from '../../components/common/LanguageSwitcher'
import type { AuthUser } from '../../types'

export default function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [messageApi, contextHolder] = message.useMessage()

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true)
    try {
      const res = await authApi.login(values)
      const user: AuthUser = {
        id: res.employee.id,
        email: values.email,
        name: res.employee.name_ja,
        employeeId: res.employee.id,
        systemRole: res.employee.system_role as AuthUser['systemRole'],
        avatarUrl: res.employee.avatar_url ?? undefined,
      }
      setAuth(user, res.access_token, res.refresh_token)
      navigate('/dashboard', { replace: true })
    } catch {
      messageApi.error(t('auth.loginFailed'))
    } finally {
      setLoading(false)
    }
  }

  const onGoogleLogin = () => {
    // TODO Phase 1: Google OAuth フロー（クライアント側 Google Sign-In SDK が必要）
    messageApi.info(t('auth.googleNotReady'))
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#f5f5f5',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      {contextHolder}

      {/* 言語切替（ログイン前でも使えるよう配置）*/}
      <div style={{ position: 'absolute', top: 16, right: 16 }}>
        <LanguageSwitcher />
      </div>

      <Card style={{ width: 400, boxShadow: '0 4px 24px rgba(0,0,0,0.08)' }}>
        <Space direction="vertical" size={24} style={{ width: '100%' }}>
          {/* ロゴ・タイトル */}
          <div style={{ textAlign: 'center' }}>
            <Typography.Title level={3} style={{ margin: 0, color: '#1677ff' }}>
              EmployeeHub
            </Typography.Title>
            <Typography.Text type="secondary" style={{ fontSize: 13 }}>
              {t('auth.tagline')}
            </Typography.Text>
          </div>

          {/* Google ログイン */}
          <Button
            icon={<GoogleOutlined />}
            size="large"
            block
            onClick={onGoogleLogin}
            style={{ borderColor: '#d9d9d9' }}
          >
            {t('auth.loginWithGoogle')}
          </Button>

          <Divider plain style={{ margin: '0' }}>
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {t('auth.or')}
            </Typography.Text>
          </Divider>

          {/* メール＋パスワード */}
          <Form layout="vertical" onFinish={onFinish} size="large">
            <Form.Item
              name="email"
              label={t('auth.email')}
              rules={[{ required: true, type: 'email' }]}
              style={{ marginBottom: 12 }}
            >
              <Input prefix={<MailOutlined />} placeholder="user@example.com" />
            </Form.Item>

            <Form.Item
              name="password"
              label={t('auth.password')}
              rules={[{ required: true }]}
              style={{ marginBottom: 4 }}
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <div style={{ textAlign: 'right', marginBottom: 16 }}>
              <Typography.Link style={{ fontSize: 13 }}>
                {t('auth.forgotPassword')}
              </Typography.Link>
            </div>

            <Form.Item style={{ marginBottom: 0 }}>
              <Button type="primary" htmlType="submit" block size="large" loading={loading}>
                {t('auth.login')}
              </Button>
            </Form.Item>
          </Form>
        </Space>
      </Card>
    </div>
  )
}
