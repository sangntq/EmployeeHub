import { Layout, Space, Button, Dropdown, Badge, Avatar, Typography } from 'antd'
import { BellOutlined, UserOutlined, LogoutOutlined, SettingOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import type { MenuProps } from 'antd'
import LanguageSwitcher from '../LanguageSwitcher'
import { useAuthStore } from '../../../stores/authStore'
import { useNotificationStore } from '../../../stores/notificationStore'

const { Header } = Layout

export default function AppHeader() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { unreadCount } = useNotificationStore()

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: t('profile.basicInfo'),
      onClick: () => user && navigate(`/employees/${user.employeeId}`),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: t('nav.settings'),
      onClick: () => navigate('/settings'),
    },
    { type: 'divider' },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('auth.logout'),
      danger: true,
      onClick: () => {
        logout()
        navigate('/login')
      },
    },
  ]

  return (
    <Header
      style={{
        background: '#fff',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #f0f0f0',
        height: 56,
        lineHeight: '56px',
      }}
    >
      {/* ロゴ */}
      <Typography.Text strong style={{ fontSize: 18, color: '#1677ff' }}>
        EmployeeHub
      </Typography.Text>

      {/* 右側メニュー */}
      <Space size={4}>
        <LanguageSwitcher />

        {/* 通知ベル */}
        <Badge count={unreadCount} size="small">
          <Button
            type="text"
            icon={<BellOutlined style={{ fontSize: 18 }} />}
            onClick={() => navigate('/notifications')}
          />
        </Badge>

        {/* ユーザーメニュー */}
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" trigger={['click']}>
          <Button type="text" style={{ padding: '0 8px', height: 40 }}>
            <Space size={8}>
              <Avatar
                size={28}
                src={user?.avatarUrl}
                icon={!user?.avatarUrl && <UserOutlined />}
              />
              <Typography.Text style={{ fontSize: 13 }}>{user?.name}</Typography.Text>
            </Space>
          </Button>
        </Dropdown>
      </Space>
    </Header>
  )
}
