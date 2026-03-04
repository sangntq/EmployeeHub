/**
 * 社員カードコンポーネント — カードビューで使用するグリッドカード
 */
import { Avatar, Card, Progress, Space, Tag, Typography } from 'antd'
import { UserOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import type { EmployeeListItem } from '../../../api/employees'

interface Props {
  employee: EmployeeListItem
  onClick: () => void
}

const AVATAR_COLORS = ['#4F46E5', '#7C3AED', '#2563EB', '#0891B2', '#059669', '#D97706', '#DC2626']

function getAvatarColor(name: string): string {
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]
}

function getInitials(nameJa: string, nameEn: string | null): string {
  if (nameEn) {
    const parts = nameEn.trim().split(/\s+/)
    return parts.length >= 2
      ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
      : nameEn.slice(0, 2).toUpperCase()
  }
  return nameJa.slice(0, 1)
}

export default function EmployeeCard({ employee, onClick }: Props) {
  const { t } = useTranslation()

  const initials = getInitials(employee.name_ja, employee.name_en)
  const avatarColor = getAvatarColor(employee.name_ja)

  const statusColor = employee.is_active ? '#10B981' : '#9CA3AF'
  const statusLabel = employee.is_active ? t('common.active') : t('common.inactive')

  return (
    <Card
      hoverable
      onClick={onClick}
      size="small"
      style={{
        borderRadius: 12,
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        cursor: 'pointer',
        border: '1px solid #E5E7EB',
      }}
      bodyStyle={{ padding: '16px' }}
    >
      {/* ヘッダー: アバター + 名前 + ステータスバッジ */}
      <Space align="start" style={{ width: '100%', marginBottom: 10 }}>
        <Avatar
          size={44}
          src={employee.avatar_url}
          icon={!employee.avatar_url && <UserOutlined />}
          style={{
            background: !employee.avatar_url ? avatarColor : undefined,
            fontWeight: 600,
            fontSize: 16,
            flexShrink: 0,
          }}
        >
          {!employee.avatar_url && initials}
        </Avatar>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <Typography.Text strong style={{ fontSize: 14, lineHeight: '1.3' }}>
              {employee.name_ja}
            </Typography.Text>
            {employee.is_mobilizable && (
              <span title={t('employee.mobilizable')} style={{ fontSize: 14 }}>✈️</span>
            )}
          </div>
          {employee.name_en && (
            <Typography.Text type="secondary" style={{ fontSize: 11 }}>
              {employee.name_en}
            </Typography.Text>
          )}
        </div>
      </Space>

      {/* タグ行: ロール・拠点・ステータス */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 10 }}>
        <Tag style={{ fontSize: 11, margin: 0 }}>{t(`role.${employee.system_role}`)}</Tag>
        <Tag color="blue" style={{ fontSize: 11, margin: 0 }}>
          {t(`officeLocation.${employee.office_location}`)}
        </Tag>
        <Tag
          style={{
            fontSize: 11,
            margin: 0,
            background: `${statusColor}20`,
            color: statusColor,
            borderColor: `${statusColor}40`,
          }}
        >
          {statusLabel}
        </Tag>
      </div>

      {/* メタ情報 */}
      <div style={{ fontSize: 12, color: '#6B7280', marginBottom: 10, lineHeight: 1.8 }}>
        {employee.department && <div>{employee.department.name_ja}</div>}
        <div>
          {t(`workStyle.${employee.work_style}`)}
          {employee.japanese_level && ` · ${t(`japaneseLevel.${employee.japanese_level}`)}`}
        </div>
      </div>

      {/* 稼働率プログレスバー */}
      {employee.workload_percent != null && (
        <div style={{ marginBottom: 4 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#6B7280', marginBottom: 2 }}>
            <span>{t('employee.workloadPercent')}</span>
            <span>{employee.workload_percent}%</span>
          </div>
          <Progress
            percent={Math.min(employee.workload_percent, 100)}
            size="small"
            showInfo={false}
            strokeColor={
              employee.workload_percent >= 100 ? '#EF4444'
              : employee.workload_percent >= 50 ? '#F59E0B'
              : '#10B981'
            }
          />
        </div>
      )}
    </Card>
  )
}
