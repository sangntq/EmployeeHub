/**
 * 社員スライドアウトパネル — Ant Design Drawer による右側詳細パネル
 * クリックした社員の基本情報・稼働状況・スキルを表示する。
 */
import { Avatar, Badge, Button, Descriptions, Drawer, Skeleton, Space, Tag, Typography } from 'antd'
import { UserOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { employeesApi } from '../../../api/employees'
import { skillsApi } from '../../../api/skills'
import { workStatusApi } from '../../../api/workStatus'

interface Props {
  employeeId: string | null
  onClose: () => void
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

const STATUS_COLORS: Record<string, string> = {
  ASSIGNED: '#4F46E5',
  FREE_IMMEDIATE: '#10B981',
  FREE_PLANNED: '#3B82F6',
  INTERNAL: '#6B7280',
  LEAVE: '#F59E0B',
  LEAVING: '#EF4444',
}

export default function EmployeeDetailPanel({ employeeId, onClose }: Props) {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const { data: employee, isLoading: loadingEmployee } = useQuery({
    queryKey: ['employee', employeeId],
    queryFn: () => employeesApi.get(employeeId!),
    enabled: !!employeeId,
  })

  const { data: workStatus } = useQuery({
    queryKey: ['workStatus', employeeId],
    queryFn: () => workStatusApi.getWorkStatus(employeeId!),
    enabled: !!employeeId,
  })

  const { data: skills } = useQuery({
    queryKey: ['employeeSkills', employeeId, 'APPROVED'],
    queryFn: () => skillsApi.listEmployeeSkills(employeeId!, 'APPROVED'),
    enabled: !!employeeId,
  })

  const topSkills = (skills ?? []).slice(0, 6)

  return (
    <Drawer
      open={!!employeeId}
      onClose={onClose}
      width={480}
      title={t('employee.detailPanel')}
      footer={
        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
          <Button onClick={onClose}>{t('action.close')}</Button>
          {employee && (
            <Button
              type="primary"
              onClick={() => {
                navigate(`/employees/${employee.id}`)
                onClose()
              }}
            >
              {t('employee.viewFullProfile')} →
            </Button>
          )}
        </Space>
      }
    >
      {loadingEmployee ? (
        <Skeleton active avatar paragraph={{ rows: 6 }} />
      ) : employee ? (
        <>
          {/* プロフィールヘッダー */}
          <Space align="center" style={{ marginBottom: 20 }}>
            <Avatar
              size={64}
              src={employee.avatar_url}
              icon={!employee.avatar_url && <UserOutlined />}
              style={{
                background: !employee.avatar_url ? getAvatarColor(employee.name_ja) : undefined,
                fontWeight: 700,
                fontSize: 22,
              }}
            >
              {!employee.avatar_url && getInitials(employee.name_ja, employee.name_en)}
            </Avatar>
            <div>
              <Typography.Title level={5} style={{ margin: 0 }}>
                {employee.name_ja}
              </Typography.Title>
              {employee.name_en && (
                <Typography.Text type="secondary" style={{ fontSize: 13 }}>
                  {employee.name_en}
                </Typography.Text>
              )}
              <div style={{ marginTop: 4 }}>
                <Tag>{employee.employee_number}</Tag>
                {employee.is_mobilizable && <Tag color="purple">✈️ {t('employee.mobilizable')}</Tag>}
              </div>
            </div>
          </Space>

          {/* 基本情報 */}
          <Descriptions column={2} size="small" bordered style={{ marginBottom: 16 }}>
            <Descriptions.Item label={t('common.officeLocation')}>
              {t(`officeLocation.${employee.office_location}`)}
            </Descriptions.Item>
            <Descriptions.Item label={t('common.workStyle')}>
              {t(`workStyle.${employee.work_style}`)}
            </Descriptions.Item>
            <Descriptions.Item label={t('common.role')}>
              <Tag>{t(`role.${employee.system_role}`)}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label={t('common.status')}>
              <Badge
                color={employee.is_active ? '#10B981' : '#9CA3AF'}
                text={employee.is_active ? t('common.active') : t('common.inactive')}
              />
            </Descriptions.Item>
            {employee.department && (
              <Descriptions.Item label={t('nav.department')} span={2}>
                {employee.department.name_ja}
              </Descriptions.Item>
            )}
            {employee.japanese_level && (
              <Descriptions.Item label={t('profile.japaneseLevel')} span={2}>
                {t(`japaneseLevel.${employee.japanese_level}`)}
              </Descriptions.Item>
            )}
          </Descriptions>

          {/* 稼働状況 */}
          {workStatus && (
            <div style={{ marginBottom: 16 }}>
              <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
                {t('workStatus.label')}
              </Typography.Text>
              <Tag
                style={{
                  background: `${STATUS_COLORS[workStatus.status] ?? '#6B7280'}15`,
                  color: STATUS_COLORS[workStatus.status] ?? '#6B7280',
                  borderColor: `${STATUS_COLORS[workStatus.status] ?? '#6B7280'}40`,
                  fontSize: 13,
                  padding: '2px 10px',
                }}
              >
                {t(`workStatus.${workStatus.status}`)}
              </Tag>
              {workStatus.free_from && (
                <Typography.Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                  {workStatus.free_from}〜
                </Typography.Text>
              )}
            </div>
          )}

          {/* スキル */}
          {topSkills.length > 0 && (
            <div>
              <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
                {t('profile.skills')} ({t('skillStatus.APPROVED')})
              </Typography.Text>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {topSkills.map(s => (
                  <Tag key={s.id} style={{ margin: 0 }}>
                    {s.skill.name_ja ?? s.skill.name}
                    {s.approved_level != null && (
                      <span style={{ marginLeft: 4, color: '#4F46E5', fontWeight: 600 }}>
                        Lv.{s.approved_level}
                      </span>
                    )}
                  </Tag>
                ))}
              </div>
            </div>
          )}
        </>
      ) : null}
    </Drawer>
  )
}
