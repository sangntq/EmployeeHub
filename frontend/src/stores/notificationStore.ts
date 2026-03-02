/**
 * 通知ストア
 *
 * 未読通知数をグローバルで管理し、AppHeader の通知バッジに表示する。
 * AppLayout のマウント時に初回フェッチし、5分ごとにポーリングする。
 */
import { create } from 'zustand'
import { notificationsApi } from '../api/notifications'

interface NotificationState {
  unreadCount: number
  setUnreadCount: (n: number) => void
  fetchUnreadCount: () => Promise<void>
}

export const useNotificationStore = create<NotificationState>((set) => ({
  unreadCount: 0,

  setUnreadCount: (n) => set({ unreadCount: n }),

  fetchUnreadCount: async () => {
    try {
      const data = await notificationsApi.getList({ is_read: false, per_page: 1 })
      set({ unreadCount: data.unread_count })
    } catch {
      // 取得失敗時はカウントを維持
    }
  },
}))
