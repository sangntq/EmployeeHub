/**
 * スキルシート出力ページ (Phase 7)
 *
 * - sales / manager 以上がアクセス可能
 * - 社員を複数選択し、Excel または PDF でダウンロード
 * - combined（1ファイル）または zip（個別ファイル）で出力
 */
import { useState } from 'react'
import {
  Card,
  Row,
  Col,
  Select,
  Button,
  Radio,
  Input,
  List,
  Avatar,
  Typography,
  notification,
} from 'antd'
import { DeleteOutlined, DownloadOutlined, UserOutlined } from '@ant-design/icons'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import PageHeader from '../../components/common/PageHeader'
import { employeesApi, type EmployeeListItem } from '../../api/employees'
import { skillsheetApi } from '../../api/skillsheet'

const { Text } = Typography

export default function SkillSheetPage() {
  const { t } = useTranslation()

  // ── 状態 ──────────────────────────────────────────────────────────────────
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [format, setFormat] = useState<'xlsx' | 'pdf'>('xlsx')
  const [outputStyle, setOutputStyle] = useState<'combined' | 'zip'>('combined')
  const [filenamePrefix, setFilenamePrefix] = useState('skillsheet')

  // ── 社員一覧取得 ──────────────────────────────────────────────────────────
  const { data: employeesData } = useQuery({
    queryKey: ['employees', 'active'],
    queryFn: () => employeesApi.list({ is_active: true, per_page: 200 }),
    staleTime: 5 * 60 * 1000,
  })

  const employees: EmployeeListItem[] = employeesData?.items ?? []
  const selectedEmployees = employees.filter(e => selectedIds.includes(e.id))

  // ── エクスポート実行 ───────────────────────────────────────────────────────
  const mutation = useMutation({
    mutationFn: skillsheetApi.export,
    onSuccess: data => {
      // バックエンドの download_url は /api/v1/skillsheet/download/{token} 形式
      // API baseURL に合わせてフルURLを組み立てる
      const baseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000/api/v1'
      const fullUrl = `${baseUrl.replace(/\/api\/v1$/, '')}${data.download_url}`
      window.open(fullUrl, '_blank')
      notification.success({ message: t('skillSheet.exportSuccess') })
    },
    onError: () => {
      notification.error({ message: t('skillSheet.exportError') })
    },
  })

  const handleDownload = () => {
    if (selectedIds.length === 0) return
    mutation.mutate({
      employee_ids: selectedIds,
      format,
      output_style: outputStyle,
      filename_prefix: filenamePrefix || 'skillsheet',
      include_salary: false,
    })
  }

  const handleRemove = (id: string) => {
    setSelectedIds(prev => prev.filter(sid => sid !== id))
  }

  // ── レンダリング ───────────────────────────────────────────────────────────
  return (
    <div style={{ padding: '24px' }}>
      <PageHeader
        title={t('skillSheet.title')}
        breadcrumbs={[{ title: t('skillSheet.title') }]}
      />

      <Row gutter={16}>
        {/* 左カラム: 候補者選択 */}
        <Col xs={24} md={14}>
          <Card title={t('skillSheet.selectedList')}>
            {/* 社員検索 Select */}
            <Select
              mode="multiple"
              showSearch
              style={{ width: '100%', marginBottom: 16 }}
              placeholder={t('skillSheet.searchEmployee')}
              filterOption={(input, option) =>
                (option?.label as string ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={employees.map(emp => ({
                value: emp.id,
                label: `${emp.name_ja}（${emp.employee_number}）`,
              }))}
              value={selectedIds}
              onChange={setSelectedIds}
              maxTagCount={0}
              maxTagPlaceholder={count =>
                t('common.selected', { count: typeof count === 'number' ? count : count.length })
              }
            />

            {/* 選択済みリスト */}
            {selectedEmployees.length === 0 ? (
              <Text type="secondary">{t('skillSheet.noEmployees')}</Text>
            ) : (
              <List
                dataSource={selectedEmployees}
                renderItem={emp => (
                  <List.Item
                    actions={[
                      <Button
                        key="remove"
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemove(emp.id)}
                      />,
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          src={emp.avatar_url ?? undefined}
                          icon={!emp.avatar_url ? <UserOutlined /> : undefined}
                        />
                      }
                      title={emp.name_ja}
                      description={emp.employee_number}
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        {/* 右カラム: 出力設定 */}
        <Col xs={24} md={10}>
          <Card title={t('skillSheet.exportConfig')}>
            {/* フォーマット */}
            <div style={{ marginBottom: 16 }}>
              <Text strong style={{ display: 'block', marginBottom: 8 }}>
                {t('skillSheet.format')}
              </Text>
              <Radio.Group value={format} onChange={e => setFormat(e.target.value)}>
                <Radio value="xlsx">{t('skillSheet.formatXlsx')}</Radio>
                <Radio value="pdf">{t('skillSheet.formatPdf')}</Radio>
              </Radio.Group>
            </div>

            {/* 出力スタイル */}
            <div style={{ marginBottom: 16 }}>
              <Text strong style={{ display: 'block', marginBottom: 8 }}>
                {t('skillSheet.outputStyle')}
              </Text>
              <Radio.Group
                value={outputStyle}
                onChange={e => setOutputStyle(e.target.value)}
              >
                <Radio value="combined" style={{ display: 'block', marginBottom: 4 }}>
                  {t('skillSheet.styleCombined')}
                </Radio>
                <Radio value="zip" style={{ display: 'block' }}>
                  {t('skillSheet.styleZip')}
                </Radio>
              </Radio.Group>
            </div>

            {/* ファイル名プレフィックス */}
            <div style={{ marginBottom: 24 }}>
              <Text strong style={{ display: 'block', marginBottom: 8 }}>
                {t('skillSheet.filenamePrefix')}
              </Text>
              <Input
                value={filenamePrefix}
                onChange={e => setFilenamePrefix(e.target.value)}
                placeholder="skillsheet"
              />
            </div>

            {/* ダウンロードボタン */}
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              size="large"
              block
              disabled={selectedIds.length === 0 || mutation.isPending}
              loading={mutation.isPending}
              onClick={handleDownload}
            >
              {t('skillSheet.download')}
            </Button>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
