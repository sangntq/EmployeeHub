/**
 * S-03 人材検索画面
 *
 * 左パネル: フィルターフォーム（スキル条件・稼働状況・拠点・勤務スタイル・日本語レベル・フリー予定日）
 * 右パネル: 検索結果カード一覧（マッチ度スコア付き）
 */
import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import {
  Row,
  Col,
  Card,
  Button,
  Select,
  Checkbox,
  DatePicker,
  Tag,
  Progress,
  Space,
  Typography,
  Avatar,
  Switch,
  InputNumber,
  Spin,
  Empty,
  Divider,
  Pagination,
  Modal,
  Input,
  message,
  Tooltip,
} from 'antd'
import {
  SearchOutlined,
  ReloadOutlined,
  UserOutlined,
  PlusOutlined,
  DeleteOutlined,
  BookOutlined,
  RobotOutlined,
  FileTextOutlined,
} from '@ant-design/icons'
import AISearchTab from './AISearchTab'
import type { Dayjs } from 'dayjs'
import { skillsApi } from '../../api/skills'
import { searchApi } from '../../api/search'
import type { SearchFilter, SearchResultItem } from '../../api/search'
import PageHeader from '../../components/common/PageHeader'

const { Text } = Typography

// ── 定数 ────────────────────────────────────────────────────────────────────────
const WORK_STATUSES = [
  'ASSIGNED',
  'FREE_IMMEDIATE',
  'FREE_PLANNED',
  'INTERNAL',
  'LEAVE',
  'LEAVING',
]
const OFFICE_LOCATIONS = ['HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER']
const WORK_STYLES = ['ONSITE', 'REMOTE', 'HYBRID']
const JAPANESE_LEVELS = ['N5', 'N4', 'N3', 'N2', 'N1', 'NATIVE']

// スキル条件の内部状態型
interface SkillCriteriaInput {
  _id: string        // リストキー用ローカルID
  skill_id: string
  level_min: number
  required: boolean
}

// ── メインページ ─────────────────────────────────────────────────────────────────
export default function SearchPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  // フィルター状態
  const [workStatuses, setWorkStatuses] = useState<string[]>([])
  const [officeLocations, setOfficeLocations] = useState<string[]>([])
  const [workStyle, setWorkStyle] = useState<string | undefined>()
  const [japaneseLevel, setJapaneseLevel] = useState<string | undefined>()
  const [freeFromBefore, setFreeFromBefore] = useState<Dayjs | null>(null)
  const [skillCriteria, setSkillCriteria] = useState<SkillCriteriaInput[]>([])

  // 左パネルのアクティブタブ（filter / ai）
  const [activeLeftTab, setActiveLeftTab] = useState<'filter' | 'ai'>('filter')

  // 検索結果
  const [searchResults, setSearchResults] = useState<{
    items: SearchResultItem[]
    total: number
  } | null>(null)
  const [currentPage, setCurrentPage] = useState(1)

  // スキルシート画面から戻った際に状態を復元する
  const SEARCH_STATE_KEY = 'employeehub_search_state'
  useEffect(() => {
    const saved = sessionStorage.getItem(SEARCH_STATE_KEY)
    if (!saved) return
    try {
      const s = JSON.parse(saved) as Record<string, unknown>
      if (Array.isArray(s.workStatuses))   setWorkStatuses(s.workStatuses as string[])
      if (Array.isArray(s.officeLocations)) setOfficeLocations(s.officeLocations as string[])
      if (s.workStyle !== undefined)       setWorkStyle(s.workStyle as string | undefined)
      if (s.japaneseLevel !== undefined)   setJapaneseLevel(s.japaneseLevel as string | undefined)
      if (s.freeFromBefore)               setFreeFromBefore(dayjs(s.freeFromBefore as string))
      if (Array.isArray(s.skillCriteria)) setSkillCriteria(s.skillCriteria as SkillCriteriaInput[])
      if (s.searchResults)                setSearchResults(s.searchResults as { items: SearchResultItem[]; total: number })
      if (typeof s.currentPage === 'number') setCurrentPage(s.currentPage)
    } catch { /* ignore */ }
  // マウント時のみ実行
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // 選択済み社員ID
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // 保存モーダル
  const [saveModalOpen, setSaveModalOpen] = useState(false)
  const [saveName, setSaveName] = useState('')

  // スキルマスタ取得
  const { data: skillMasters } = useQuery({
    queryKey: ['skillMasters'],
    queryFn: skillsApi.listMasters,
  })
  const allSkills = skillMasters?.categories.flatMap(c => c.skills) ?? []

  // 検索実行
  const searchMutation = useMutation({
    mutationFn: searchApi.filter,
    onSuccess: data => {
      setSearchResults({ items: data.items, total: data.total })
      setCurrentPage(data.page)
      setSelectedIds(new Set())  // 検索のたびに選択リセット
    },
    onError: () => {
      void message.error(t('common.error'))
    },
  })

  // 検索条件保存
  const saveMutation = useMutation({
    mutationFn: searchApi.saveCriteria,
    onSuccess: () => {
      void message.success(t('search.searchSaved'))
      setSaveModalOpen(false)
      setSaveName('')
    },
    onError: () => {
      void message.error(t('common.error'))
    },
  })

  // フィルターオブジェクト生成
  const buildFilter = (page = 1): SearchFilter => ({
    skills: skillCriteria
      .filter(sc => sc.skill_id)
      .map(sc => ({
        skill_id: sc.skill_id,
        level_min: sc.level_min,
        required: sc.required,
      })),
    work_statuses: workStatuses,
    office_locations: officeLocations,
    work_style: workStyle,
    japanese_level: japaneseLevel,
    free_from_before: freeFromBefore ? freeFromBefore.format('YYYY-MM-DD') : undefined,
    page,
    per_page: 20,
  })

  const handleSearch = (page = 1) => {
    searchMutation.mutate(buildFilter(page))
  }

  const handleAISearch = (criteria: SearchFilter) => {
    searchMutation.mutate({ ...criteria, page: 1, per_page: 20 })
  }

  const saveStateToSession = () => {
    sessionStorage.setItem(SEARCH_STATE_KEY, JSON.stringify({
      workStatuses,
      officeLocations,
      workStyle,
      japaneseLevel,
      freeFromBefore: freeFromBefore?.toISOString() ?? null,
      skillCriteria,
      searchResults,
      currentPage,
    }))
  }

  const handleReset = () => {
    sessionStorage.removeItem(SEARCH_STATE_KEY)
    setWorkStatuses([])
    setOfficeLocations([])
    setWorkStyle(undefined)
    setJapaneseLevel(undefined)
    setFreeFromBefore(null)
    setSkillCriteria([])
    setSearchResults(null)
    setCurrentPage(1)
    setSelectedIds(new Set())
  }

  // 選択操作
  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const currentItems = searchResults?.items ?? []
  const allCurrentSelected =
    currentItems.length > 0 && currentItems.every(item => selectedIds.has(item.employee.id))
  const someCurrentSelected =
    currentItems.some(item => selectedIds.has(item.employee.id)) && !allCurrentSelected

  const toggleSelectAll = () => {
    if (allCurrentSelected) {
      setSelectedIds(prev => {
        const next = new Set(prev)
        currentItems.forEach(item => next.delete(item.employee.id))
        return next
      })
    } else {
      setSelectedIds(prev => {
        const next = new Set(prev)
        currentItems.forEach(item => next.add(item.employee.id))
        return next
      })
    }
  }

  const handleExportSkillSheet = () => {
    saveStateToSession()
    // 選択済み社員のスナップショットも一緒に渡す（SkillSheet側でper_page上限に依存しないため）
    const snapshots = currentItems
      .filter(item => selectedIds.has(item.employee.id))
      .map(item => ({
        id: item.employee.id,
        name_ja: item.employee.name_ja,
        employee_number: item.employee.employee_number,
        avatar_url: item.employee.avatar_url ?? null,
      }))
    navigate('/skillsheet', { state: { employee_ids: [...selectedIds], imported_employees: snapshots } })
  }

  const handleSaveSearch = () => {
    if (!saveName.trim()) return
    saveMutation.mutate({
      name: saveName.trim(),
      criteria: buildFilter() as Record<string, unknown>,
    })
  }

  // スキル条件の追加・削除・更新
  const addSkillCriteria = () => {
    setSkillCriteria(prev => [
      ...prev,
      { _id: Math.random().toString(36).slice(2), skill_id: '', level_min: 1, required: true },
    ])
  }

  const removeSkillCriteria = (_id: string) => {
    setSkillCriteria(prev => prev.filter(sc => sc._id !== _id))
  }

  const updateSkillCriteria = (_id: string, updates: Partial<Omit<SkillCriteriaInput, '_id'>>) => {
    setSkillCriteria(prev =>
      prev.map(sc => (sc._id === _id ? { ...sc, ...updates } : sc))
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <PageHeader
        title={t('search.title')}
        breadcrumbs={[{ title: t('page.search') }]}
      />

      <Row gutter={16} style={{ marginTop: 16 }}>
        {/* ── 左パネル: フィルター / AI検索 タブ ──────────────────────── */}
        <Col span={7}>
          <Card
            size="small"
            tabList={[
              { key: 'filter', tab: t('aiSearch.filterTab') },
              {
                key: 'ai',
                tab: (
                  <span>
                    <RobotOutlined style={{ marginRight: 4 }} />
                    {t('aiSearch.tab')}
                  </span>
                ),
              },
            ]}
            activeTabKey={activeLeftTab}
            onTabChange={k => setActiveLeftTab(k as 'filter' | 'ai')}
          >
            {activeLeftTab === 'ai' ? (
              <AISearchTab onSearch={handleAISearch} />
            ) : (
              <>
            {/* スキル条件 */}
            <div style={{ marginBottom: 12 }}>
              <Text strong style={{ fontSize: 13 }}>{t('search.skill')}</Text>
              <div style={{ marginTop: 8 }}>
                {skillCriteria.map(sc => (
                  <div
                    key={sc._id}
                    style={{
                      background: '#fafafa',
                      border: '1px solid #e8e8e8',
                      borderRadius: 6,
                      padding: '8px 10px',
                      marginBottom: 8,
                    }}
                  >
                    <Row gutter={4} align="middle" style={{ marginBottom: 6 }}>
                      <Col flex="auto">
                        <Select
                          showSearch
                          placeholder={t('skill.selectSkillPlaceholder')}
                          filterOption={(input, option) =>
                            (option?.label as string ?? '').toLowerCase().includes(input.toLowerCase())
                          }
                          value={sc.skill_id || undefined}
                          onChange={v => updateSkillCriteria(sc._id, { skill_id: v })}
                          style={{ width: '100%' }}
                          size="small"
                          options={allSkills.map(s => ({
                            value: s.id,
                            label: s.name_ja || s.name,
                          }))}
                        />
                      </Col>
                      <Col>
                        <Button
                          type="text"
                          danger
                          size="small"
                          icon={<DeleteOutlined />}
                          onClick={() => removeSkillCriteria(sc._id)}
                        />
                      </Col>
                    </Row>
                    <Row gutter={6} align="middle">
                      <Col>
                        <Text type="secondary" style={{ fontSize: 11 }}>{t('search.levelMin')}</Text>
                      </Col>
                      <Col>
                        <InputNumber
                          min={1}
                          max={5}
                          size="small"
                          value={sc.level_min}
                          onChange={v => updateSkillCriteria(sc._id, { level_min: v ?? 1 })}
                          style={{ width: 52 }}
                        />
                      </Col>
                      <Col flex="auto" style={{ textAlign: 'right' }}>
                        <Switch
                          size="small"
                          checked={sc.required}
                          onChange={v => updateSkillCriteria(sc._id, { required: v })}
                          checkedChildren={t('search.required')}
                          unCheckedChildren={t('search.optional')}
                        />
                      </Col>
                    </Row>
                  </div>
                ))}
                <Button
                  type="dashed"
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={addSkillCriteria}
                  block
                >
                  {t('search.addSkill')}
                </Button>
              </div>
            </div>

            <Divider style={{ margin: '10px 0' }} />

            {/* 稼働状況 */}
            <div style={{ marginBottom: 12 }}>
              <Text strong style={{ fontSize: 13 }}>{t('search.workStatus')}</Text>
              <div style={{ marginTop: 6 }}>
                <Checkbox.Group
                  value={workStatuses}
                  onChange={v => setWorkStatuses(v as string[])}
                  style={{ display: 'flex', flexDirection: 'column', gap: 2 }}
                >
                  {WORK_STATUSES.map(s => (
                    <Checkbox key={s} value={s}>
                      <Text style={{ fontSize: 12 }}>{t(`workStatus.${s}`)}</Text>
                    </Checkbox>
                  ))}
                </Checkbox.Group>
              </div>
            </div>

            <Divider style={{ margin: '10px 0' }} />

            {/* 拠点 */}
            <div style={{ marginBottom: 12 }}>
              <Text strong style={{ fontSize: 13 }}>{t('search.officeLocation')}</Text>
              <div style={{ marginTop: 6 }}>
                <Checkbox.Group
                  value={officeLocations}
                  onChange={v => setOfficeLocations(v as string[])}
                  style={{ display: 'flex', flexDirection: 'column', gap: 2 }}
                >
                  {OFFICE_LOCATIONS.map(loc => (
                    <Checkbox key={loc} value={loc}>
                      <Text style={{ fontSize: 12 }}>{t(`officeLocation.${loc}`)}</Text>
                    </Checkbox>
                  ))}
                </Checkbox.Group>
              </div>
            </div>

            <Divider style={{ margin: '10px 0' }} />

            {/* 勤務スタイル */}
            <div style={{ marginBottom: 10 }}>
              <Text strong style={{ fontSize: 13 }}>{t('search.workStyle')}</Text>
              <Select
                allowClear
                placeholder={t('common.all')}
                value={workStyle}
                onChange={setWorkStyle}
                style={{ width: '100%', marginTop: 4 }}
                size="small"
                options={WORK_STYLES.map(ws => ({
                  value: ws,
                  label: t(`workStyle.${ws}`),
                }))}
              />
            </div>

            {/* 日本語レベル */}
            <div style={{ marginBottom: 10 }}>
              <Text strong style={{ fontSize: 13 }}>{t('search.japaneseLevel')}</Text>
              <Select
                allowClear
                placeholder={t('common.all')}
                value={japaneseLevel}
                onChange={setJapaneseLevel}
                style={{ width: '100%', marginTop: 4 }}
                size="small"
                options={JAPANESE_LEVELS.map(lv => ({
                  value: lv,
                  label: t(`japaneseLevel.${lv}`),
                }))}
              />
            </div>

            {/* フリー予定日 */}
            <div style={{ marginBottom: 14 }}>
              <Text strong style={{ fontSize: 13 }}>{t('search.freeFromBefore')}</Text>
              <DatePicker
                allowClear
                value={freeFromBefore}
                onChange={setFreeFromBefore}
                style={{ width: '100%', marginTop: 4 }}
                size="small"
              />
            </div>

            <Divider style={{ margin: '10px 0' }} />

            {/* アクションボタン */}
            <Space direction="vertical" style={{ width: '100%' }} size={6}>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={() => handleSearch(1)}
                loading={searchMutation.isPending}
                block
              >
                {t('search.doSearch')}
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
                block
              >
                {t('search.reset')}
              </Button>
              {searchResults && (
                <Button
                  icon={<BookOutlined />}
                  onClick={() => setSaveModalOpen(true)}
                  block
                >
                  {t('search.saveSearch')}
                </Button>
              )}
            </Space>
              </>
            )}
          </Card>
        </Col>

        {/* ── 右パネル: 検索結果 ──────────────────────────────────────── */}
        <Col span={17}>

          {/* ローディング */}
          {searchMutation.isPending && (
            <div style={{ textAlign: 'center', padding: 80 }}>
              <Spin size="large" />
            </div>
          )}

          {/* 初期状態（未検索） */}
          {!searchMutation.isPending && !searchResults && (
            <div
              style={{
                textAlign: 'center',
                padding: '80px 0',
                color: '#bfbfbf',
              }}
            >
              <SearchOutlined style={{ fontSize: 56, display: 'block', marginBottom: 16 }} />
              <Text type="secondary">{t('search.hint')}</Text>
            </div>
          )}

          {/* 結果表示 */}
          {!searchMutation.isPending && searchResults && (
            <>
              {/* 結果件数 + 選択ツールバー */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 12,
                  minHeight: 32,
                }}
              >
                <Space>
                  <Text type="secondary" style={{ fontSize: 13 }}>
                    {t('search.resultCount', { count: searchResults.total })}
                  </Text>
                  {searchResults.items.length > 0 && (
                    <Checkbox
                      indeterminate={someCurrentSelected}
                      checked={allCurrentSelected}
                      onChange={toggleSelectAll}
                    >
                      <Text style={{ fontSize: 12 }}>{t('search.selectAll')}</Text>
                    </Checkbox>
                  )}
                </Space>
                {selectedIds.size > 0 && (
                  <Space>
                    <Text style={{ fontSize: 12, color: '#1677ff' }}>
                      {t('search.selectedCount', { count: selectedIds.size })}
                    </Text>
                    <Tooltip title={t('search.exportToSkillSheetTooltip')}>
                      <Button
                        type="primary"
                        icon={<FileTextOutlined />}
                        size="small"
                        onClick={handleExportSkillSheet}
                      >
                        {t('search.exportToSkillSheet')}
                      </Button>
                    </Tooltip>
                  </Space>
                )}
              </div>

              {searchResults.items.length === 0 ? (
                <Empty description={t('search.noResults')} />
              ) : (
                <Row gutter={[12, 12]}>
                  {searchResults.items.map(item => (
                    <Col span={12} key={item.employee.id}>
                      <ResultCard
                        item={item}
                        selected={selectedIds.has(item.employee.id)}
                        onToggleSelect={() => toggleSelect(item.employee.id)}
                        onView={() => navigate(`/employees/${item.employee.id}`)}
                      />
                    </Col>
                  ))}
                </Row>
              )}

              {/* ページネーション */}
              {searchResults.total > 20 && (
                <div style={{ marginTop: 20, textAlign: 'center' }}>
                  <Pagination
                    current={currentPage}
                    total={searchResults.total}
                    pageSize={20}
                    onChange={page => handleSearch(page)}
                    showSizeChanger={false}
                  />
                </div>
              )}
            </>
          )}
        </Col>
      </Row>

      {/* 保存モーダル */}
      <Modal
        title={t('search.saveSearch')}
        open={saveModalOpen}
        onOk={handleSaveSearch}
        onCancel={() => {
          setSaveModalOpen(false)
          setSaveName('')
        }}
        confirmLoading={saveMutation.isPending}
        okText={t('action.save')}
        cancelText={t('action.cancel')}
      >
        <Input
          placeholder={t('search.saveNamePlaceholder')}
          value={saveName}
          onChange={e => setSaveName(e.target.value)}
          onPressEnter={handleSaveSearch}
          style={{ marginTop: 8 }}
        />
      </Modal>
    </div>
  )
}

// ── 結果カードコンポーネント ──────────────────────────────────────────────────────
interface ResultCardProps {
  item: SearchResultItem
  selected: boolean
  onToggleSelect: () => void
  onView: () => void
}

function ResultCard({ item, selected, onToggleSelect, onView }: ResultCardProps) {
  const { t } = useTranslation()
  const { employee, work_status, match_score, matched_skills, missing_skills } = item

  const scoreColor =
    match_score >= 80 ? '#52c41a' : match_score >= 50 ? '#faad14' : '#ff4d4f'

  const statusColor =
    work_status?.status === 'FREE_IMMEDIATE' || work_status?.status === 'FREE_PLANNED'
      ? 'green'
      : work_status?.status === 'ASSIGNED'
        ? 'blue'
        : 'default'

  return (
    <Card
      size="small"
      hoverable
      onClick={onToggleSelect}
      style={{
        height: '100%',
        cursor: 'pointer',
        outline: selected ? '2px solid #1677ff' : '2px solid transparent',
        outlineOffset: -1,
        transition: 'outline-color 0.15s',
      }}
      actions={[
        <Checkbox
          key="select"
          checked={selected}
          onChange={onToggleSelect}
          onClick={e => e.stopPropagation()}
        >
          <span style={{ fontSize: 12 }}>{t('search.select')}</span>
        </Checkbox>,
        <Button
          type="link"
          key="view"
          style={{ fontSize: 13 }}
          onClick={e => { e.stopPropagation(); onView() }}
        >
          {t('search.viewProfile')}
        </Button>,
      ]}
    >
      <Row gutter={10} align="top" wrap={false}>
        <Col>
          <Avatar
            size={46}
            src={employee.avatar_url}
            icon={<UserOutlined />}
            style={{ background: '#e6f4ff', color: '#1677ff', flexShrink: 0 }}
          />
        </Col>
        <Col flex="auto" style={{ minWidth: 0 }}>
          <div
            style={{
              fontWeight: 600,
              fontSize: 14,
              lineHeight: '20px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {employee.name_ja}
          </div>
          <Text type="secondary" style={{ fontSize: 11 }}>
            {employee.employee_number}
            {employee.name_en && ` / ${employee.name_en}`}
          </Text>
          {employee.department && (
            <div>
              <Text type="secondary" style={{ fontSize: 11 }}>
                {employee.department.name_ja}
              </Text>
            </div>
          )}
        </Col>
        <Col style={{ flexShrink: 0 }}>
          <div style={{ textAlign: 'center' }}>
            <Progress
              type="circle"
              size={50}
              percent={match_score}
              strokeColor={scoreColor}
              format={p => (
                <span style={{ fontSize: 11, fontWeight: 700, color: scoreColor }}>
                  {p}%
                </span>
              )}
            />
            <div style={{ fontSize: 10, color: '#8c8c8c', marginTop: 2 }}>
              {t('search.matchScore')}
            </div>
          </div>
        </Col>
      </Row>

      {/* ステータス・拠点タグ */}
      <div style={{ marginTop: 8 }}>
        <Space size={3} wrap>
          {work_status && (
            <Tag color={statusColor} style={{ fontSize: 11, margin: 0 }}>
              {t(`workStatus.${work_status.status}`)}
            </Tag>
          )}
          <Tag style={{ fontSize: 11, margin: 0 }}>
            {t(`officeLocation.${employee.office_location}`)}
          </Tag>
          <Tag style={{ fontSize: 11, margin: 0 }}>
            {t(`workStyle.${employee.work_style}`)}
          </Tag>
          {employee.japanese_level && employee.japanese_level !== 'NONE' && (
            <Tag color="purple" style={{ fontSize: 11, margin: 0 }}>
              {t(`japaneseLevel.${employee.japanese_level}`)}
            </Tag>
          )}
        </Space>
      </div>

      {/* マッチ・未マッチスキルタグ */}
      {(matched_skills.length > 0 || missing_skills.length > 0) && (
        <div style={{ marginTop: 6 }}>
          <Space size={3} wrap>
            {matched_skills.map(s => (
              <Tag key={s} color="success" style={{ fontSize: 11, margin: 0 }}>
                {s}
              </Tag>
            ))}
            {missing_skills.map(s => (
              <Tag key={s} color="error" style={{ fontSize: 11, margin: 0 }}>
                {s}
              </Tag>
            ))}
          </Space>
        </div>
      )}
    </Card>
  )
}
