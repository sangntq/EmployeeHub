import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  SearchOutlined,
  TeamOutlined,
  CheckSquareOutlined,
  FileTextOutlined,
  BellOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { useNavigate, useLocation } from 'react-router-dom'
import type { MenuProps } from 'antd'
import { useAuthStore } from '../../../stores/authStore'

const { Sider } = Layout

// 管理者のみに表示するメニューキー
const ADMIN_ONLY_KEYS = ['settings']
// manager以上のみに表示するメニューキー
const MANAGER_PLUS_KEYS = ['approvals', 'alerts']
// sales以上（member以外）に表示するメニューキー
const SALES_PLUS_KEYS = ['skillsheet']

export default function Sidebar() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuthStore()

  // 現在のパスからアクティブなメニューキーを判定
  const selectedKey = location.pathname.split('/')[1] || 'dashboard'

  const allItems: MenuProps['items'] = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: t('nav.dashboard'),
    },
    {
      key: 'search',
      icon: <SearchOutlined />,
      label: t('nav.search'),
    },
    {
      key: 'employees',
      icon: <TeamOutlined />,
      label: t('nav.employees'),
    },
    {
      key: 'approvals',
      icon: <CheckSquareOutlined />,
      label: t('nav.approvals'),
    },
    {
      key: 'skillsheet',
      icon: <FileTextOutlined />,
      label: t('nav.skillSheet'),
    },
    {
      key: 'alerts',
      icon: <BellOutlined />,
      label: t('nav.alerts'),
    },
    {
      key: 'notifications',
      icon: <BellOutlined />,
      label: t('nav.notifications'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: t('nav.settings'),
    },
  ]

  const managerPlusRoles = ['manager', 'department_head', 'director', 'admin']
  const salesPlusRoles = ['sales', 'manager', 'department_head', 'director', 'admin']

  // member・sales はアクセス不可メニューを除外
  const items = allItems.filter((item) => {
    if (!item || !('key' in item)) return true
    const key = item.key as string
    if (ADMIN_ONLY_KEYS.includes(key)) {
      return user?.systemRole === 'admin'
    }
    if (MANAGER_PLUS_KEYS.includes(key)) {
      return user?.systemRole != null && managerPlusRoles.includes(user.systemRole)
    }
    if (SALES_PLUS_KEYS.includes(key)) {
      return user?.systemRole != null && salesPlusRoles.includes(user.systemRole)
    }
    return true
  })

  return (
    <Sider
      width={220}
      style={{
        background: '#fff',
        borderRight: '1px solid #f0f0f0',
        overflow: 'auto',
        height: '100vh',
        position: 'sticky',
        top: 0,
      }}
    >
      {/* ロゴスペーサー（ヘッダーと高さを合わせる）*/}
      <div style={{ height: 56, borderBottom: '1px solid #f0f0f0' }} />

      <Menu
        mode="inline"
        selectedKeys={[selectedKey]}
        style={{ border: 'none', paddingTop: 8 }}
        items={items}
        onClick={({ key }) => navigate(`/${key}`)}
      />
    </Sider>
  )
}
