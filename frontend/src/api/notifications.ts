/**
 * 通知 API クライアント
 */
import apiClient from './client'

export interface NotificationItem {
  id: string
  type: string
  title: string
  body: string | null
  is_read: boolean
  related_entity_type: string | null
  related_entity_id: string | null
  created_at: string
}

export interface NotificationListResponse {
  items: NotificationItem[]
  total: number
  unread_count: number
  page: number
  per_page: number
}

export const notificationsApi = {
  getList: (params?: { is_read?: boolean; page?: number; per_page?: number }) =>
    apiClient
      .get<NotificationListResponse>('/notifications', { params })
      .then((r) => r.data),

  markAsRead: (id: string) =>
    apiClient.patch(`/notifications/${id}/read`),

  markAllRead: () =>
    apiClient.patch('/notifications/read-all'),
}
