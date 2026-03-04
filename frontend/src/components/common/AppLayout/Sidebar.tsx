import { useState } from 'react'
import { Layout, Menu, Tooltip } from 'antd'
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { useNavigate, useLocation } from 'react-router-dom'
import type { MenuProps } from 'antd'
import { useAuthStore } from '../../../stores/authStore'

const { Sider } = Layout

// 絵文字アイコンのラッパー（mockup スタイル）
const EmojiIcon = ({ e }: { e: string }) => (
  <span
    style={{
      fontSize: 17,
      lineHeight: 1,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: 20,
      height: 20,
    }}
  >
    {e}
  </span>
)

export default function Sidebar() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuthStore()
  const [collapsed, setCollapsed] = useState(false)

  const managerPlusRoles = ['manager', 'department_head', 'director', 'admin']
  const salesPlusRoles = ['sales', 'manager', 'department_head', 'director', 'admin']
  const isManagerPlus = user?.systemRole != null && managerPlusRoles.includes(user.systemRole)
  const isSalesPlus = user?.systemRole != null && salesPlusRoles.includes(user.systemRole)
  const isAdmin = user?.systemRole === 'admin'

  // 現在のパスからアクティブなメニューキーを判定
  const selectedKey = (() => {
    if (user?.employeeId && location.pathname === `/employees/${user.employeeId}`) {
      return 'my-profile'
    }
    return location.pathname.split('/')[1] || 'dashboard'
  })()

  const items: MenuProps['items'] = []

  // ── Sales Tools グループ (sales以上) ──────────────────────────
  if (isSalesPlus) {
    items.push({
      type: 'group',
      label: t('nav.group.salesTools'),
      children: [
        { key: 'search',       icon: <EmojiIcon e="🤖" />, label: t('nav.search') },
        { key: 'availability', icon: <EmojiIcon e="📅" />, label: t('nav.availability') },
        { key: 'skills',       icon: <EmojiIcon e="📈" />, label: t('nav.skills') },
        { key: 'skillsheet',   icon: <EmojiIcon e="📄" />, label: t('nav.skillSheet') },
      ],
    })
  }

  // ── Management グループ (manager以上) ──────────────────────────
  if (isManagerPlus) {
    items.push({
      type: 'group',
      label: t('nav.group.management'),
      children: [
        { key: 'dashboard',     icon: <EmojiIcon e="🏠" />, label: t('nav.dashboard') },
        { key: 'employees',     icon: <EmojiIcon e="👥" />, label: t('nav.employees') },
        { key: 'certifications',icon: <EmojiIcon e="🏅" />, label: t('nav.certifications') },
        { key: 'approvals',     icon: <EmojiIcon e="✅" />, label: t('nav.approvals') },
        { key: 'alerts',        icon: <EmojiIcon e="⚠️" />, label: t('nav.alerts') },
      ],
    })
  }

  // ── Personal グループ (全ロール) ───────────────────────────────
  items.push({
    type: 'group',
    label: t('nav.group.personal'),
    children: [
      ...(user?.employeeId
        ? [{ key: 'my-profile', icon: <EmojiIcon e="✏️" />, label: t('nav.myProfile') }]
        : []),
      { key: 'notifications', icon: <EmojiIcon e="🔔" />, label: t('nav.notifications') },
    ],
  })

  // ── System グループ (admin only) ───────────────────────────────
  if (isAdmin) {
    items.push({
      type: 'group',
      label: t('nav.group.system'),
      children: [
        { key: 'settings', icon: <EmojiIcon e="⚙️" />, label: t('nav.settings') },
      ],
    })
  }

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'my-profile' && user?.employeeId) {
      navigate(`/employees/${user.employeeId}`)
    } else {
      navigate(`/${key}`)
    }
  }

  return (
    <>
      {/* グループラベルのスタイル上書き */}
      <style>{`
        /* ── 展開時 ─────────────────────────────────────── */
        .sidebar-menu .ant-menu-item-group-title {
          color: rgba(255, 255, 255, 0.35) !important;
          font-size: 10px !important;
          font-weight: 600 !important;
          letter-spacing: 0.08em !important;
          text-transform: uppercase !important;
          padding: 14px 16px 4px !important;
          white-space: nowrap;
          overflow: hidden;
        }
        .sidebar-menu .ant-menu-item {
          border-radius: 8px !important;
          margin: 2px 8px !important;
          width: calc(100% - 16px) !important;
        }

        /* ── 収縮時：グループラベルを完全に非表示 ────────── */
        .sidebar-menu.ant-menu-inline-collapsed .ant-menu-item-group-title {
          display: none !important;
        }
        /* 収縮時：アイテムをアイコンのみ中央配置 */
        .sidebar-menu.ant-menu-inline-collapsed .ant-menu-item {
          margin: 2px auto !important;
          width: 40px !important;
          padding: 0 !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
        }
        /* 収縮時：ラベルテキストを非表示 */
        .sidebar-menu.ant-menu-inline-collapsed .ant-menu-title-content {
          display: none !important;
        }
        /* 収縮時：アイコンのみ表示 */
        .sidebar-menu.ant-menu-inline-collapsed .ant-menu-item .anticon,
        .sidebar-menu.ant-menu-inline-collapsed .ant-menu-item > span:first-child {
          margin: 0 !important;
          font-size: 18px !important;
        }

        .sidebar-toggle-btn:hover {
          background: rgba(255,255,255,0.15) !important;
          color: white !important;
        }
      `}</style>

      <Sider
        width={220}
        collapsedWidth={64}
        collapsed={collapsed}
        style={{
          background: '#1E1B4B',
          height: '100vh',
          position: 'sticky',
          top: 0,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* ── ロゴエリア ── */}
        <div
          style={{
            height: 56,
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'flex-start',
            paddingLeft: collapsed ? 0 : 20,
            borderBottom: '1px solid rgba(255,255,255,0.1)',
            flexShrink: 0,
            overflow: 'hidden',
            transition: 'padding 0.2s',
          }}
        >
          {collapsed ? (
            <div
              style={{
                width: 32,
                height: 32,
                background: '#4F46E5',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 16,
              }}
            >
              🏢
            </div>
          ) : (
            <span style={{ color: '#fff', fontWeight: 700, fontSize: 16, letterSpacing: '-0.3px' }}>
              Employee<span style={{ color: '#818CF8' }}>Hub</span>
            </span>
          )}
        </div>

        {/* ── ナビメニュー（スクロール可能） ── */}
        <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
          <Menu
            theme="dark"
            mode="inline"
            inlineCollapsed={collapsed}
            selectedKeys={[selectedKey]}
            className="sidebar-menu"
            style={{ border: 'none', paddingTop: 8, background: '#1E1B4B' }}
            items={items}
            onClick={handleMenuClick}
          />
        </div>

        {/* ── 折りたたみトグルボタン ── */}
        <div
          style={{
            flexShrink: 0,
            borderTop: '1px solid rgba(255,255,255,0.1)',
            padding: '10px 12px',
            display: 'flex',
            justifyContent: collapsed ? 'center' : 'flex-end',
          }}
        >
          <Tooltip
            title={collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')}
            placement="right"
          >
            <button
              className="sidebar-toggle-btn"
              onClick={() => setCollapsed((c) => !c)}
              style={{
                background: 'rgba(255,255,255,0.08)',
                border: 'none',
                borderRadius: 8,
                color: 'rgba(255,255,255,0.6)',
                cursor: 'pointer',
                width: 32,
                height: 32,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 14,
                transition: 'background 0.15s, color 0.15s',
                flexShrink: 0,
              }}
            >
              {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </button>
          </Tooltip>
        </div>
      </Sider>
    </>
  )
}
