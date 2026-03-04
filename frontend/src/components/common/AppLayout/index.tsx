import { useEffect, useRef } from 'react'
import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'
import AppHeader from './AppHeader'
import Sidebar from './Sidebar'
import { useNotificationStore } from '../../../stores/notificationStore'
import { useAuthStore } from '../../../stores/authStore'

const { Content } = Layout

const POLL_INTERVAL_MS = 5 * 60 * 1000 // 5分

export default function AppLayout() {
  const { fetchUnreadCount } = useNotificationStore()
  const { isAuthenticated } = useAuthStore()
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!isAuthenticated) return

    // 初回フェッチ
    fetchUnreadCount()

    // 5分ごとにポーリング
    timerRef.current = setInterval(fetchUnreadCount, POLL_INTERVAL_MS)

    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isAuthenticated, fetchUnreadCount])

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 左サイドバー */}
      <Sidebar />

      <Layout>
        {/* トップヘッダー */}
        <AppHeader />

        {/* メインコンテンツ */}
        <Content
          style={{
            padding: 24,
            background: '#F9FAFB',
            minHeight: 'calc(100vh - 56px)',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
