/**
 * 通知一覧ページ (S-09)
 *
 * 自分宛の通知を一覧表示し、既読操作・全件既読を提供する。
 * 全ロールからアクセス可能。
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { List, Button, Typography, Skeleton, Alert, Space, Tag } from 'antd'
import { CheckOutlined } from '@ant-design/icons'
import { notificationsApi } from '../../api/notifications'
import type { NotificationItem } from '../../api/notifications'
import { useNotificationStore } from '../../stores/notificationStore'
import PageHeader from '../../components/common/PageHeader'

const STALE_TIME = 60 * 1000 // 1分

export default function NotificationsPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const { fetchUnreadCount } = useNotificationStore()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.getList({ per_page: 50 }),
    staleTime: STALE_TIME,
  })

  const markAsReadMutation = useMutation({
    mutationFn: (id: string) => notificationsApi.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      fetchUnreadCount()
    },
  })

  const markAllReadMutation = useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      fetchUnreadCount()
    },
  })

  const items = data?.items ?? []

  if (isLoading) {
    return (
      <div>
        <PageHeader title={t('notification.title')} />
        <Skeleton active paragraph={{ rows: 6 }} />
      </div>
    )
  }

  if (isError) {
    return (
      <div>
        <PageHeader title={t('notification.title')} />
        <Alert type="error" message={t('common.error')} />
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title={t('notification.title')}
        extra={
          <Button
            onClick={() => markAllReadMutation.mutate()}
            loading={markAllReadMutation.isPending}
            disabled={items.every((n) => n.is_read)}
          >
            {t('notification.markAllRead')}
          </Button>
        }
      />

      <List<NotificationItem>
        dataSource={items}
        locale={{ emptyText: t('notification.noNotifications') }}
        renderItem={(item) => (
          <List.Item
            key={item.id}
            style={{
              background: item.is_read ? undefined : '#e6f4ff',
              padding: '12px 16px',
              marginBottom: 4,
              borderRadius: 6,
            }}
            actions={[
              !item.is_read ? (
                <Button
                  key="read"
                  size="small"
                  icon={<CheckOutlined />}
                  loading={markAsReadMutation.isPending && markAsReadMutation.variables === item.id}
                  onClick={() => markAsReadMutation.mutate(item.id)}
                >
                  {t('notification.markAsRead')}
                </Button>
              ) : null,
            ].filter(Boolean)}
          >
            <List.Item.Meta
              title={
                <Space size={8}>
                  {!item.is_read && <Tag color="blue" style={{ margin: 0 }} />}
                  <Typography.Text strong={!item.is_read}>{item.title}</Typography.Text>
                </Space>
              }
              description={
                <Space direction="vertical" size={2}>
                  {item.body && (
                    <Typography.Text type="secondary">{item.body}</Typography.Text>
                  )}
                  <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    {new Date(item.created_at).toLocaleString()}
                  </Typography.Text>
                </Space>
              }
            />
          </List.Item>
        )}
      />
    </div>
  )
}
