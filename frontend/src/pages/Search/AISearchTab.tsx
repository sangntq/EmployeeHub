/**
 * S-04 AI自然言語検索タブ
 *
 * 顧客要件テキストを貼り付け → AI解析 → 条件を確認 → 検索実行
 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import {
  Button,
  Input,
  Alert,
  Space,
  Tag,
  Typography,
  Divider,
  Spin,
  Row,
  Col,
} from 'antd'
import {
  RobotOutlined,
  SearchOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import { searchApi } from '../../api/search'
import type { AIParseResponse, SearchFilter } from '../../api/search'

const { TextArea } = Input
const { Text } = Typography

interface AISearchTabProps {
  /** 検索実行コールバック（criteriaを受け取りfilter検索に渡す） */
  onSearch: (criteria: SearchFilter) => void
}

export default function AISearchTab({ onSearch }: AISearchTabProps) {
  const { t } = useTranslation()
  const [inputText, setInputText] = useState('')
  const [parseResult, setParseResult] = useState<AIParseResponse | null>(null)

  const parseMutation = useMutation({
    mutationFn: () => searchApi.aiParse(inputText),
    onSuccess: data => {
      setParseResult(data)
    },
  })

  const handleParse = () => {
    if (!inputText.trim()) return
    setParseResult(null)
    parseMutation.mutate()
  }

  const handleSearch = () => {
    if (!parseResult) return
    onSearch(parseResult.criteria)
  }

  // サービス無効（503）チェック
  const isDisabled =
    parseMutation.isError &&
    (parseMutation.error as { response?: { status?: number } })?.response?.status === 503

  return (
    <div style={{ padding: '0 4px' }}>
      {/* テキスト入力エリア */}
      <div style={{ marginBottom: 12 }}>
        <Text strong style={{ fontSize: 13 }}>
          {t('aiSearch.inputLabel')}
        </Text>
        <TextArea
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          placeholder={t('aiSearch.inputPlaceholder')}
          rows={5}
          style={{ marginTop: 6, resize: 'vertical' }}
          maxLength={5000}
          showCount
        />
      </div>

      <Button
        type="primary"
        icon={<RobotOutlined />}
        onClick={handleParse}
        loading={parseMutation.isPending}
        disabled={!inputText.trim()}
        style={{ marginBottom: 16 }}
      >
        {t('aiSearch.parseButton')}
      </Button>

      {/* サービス無効メッセージ */}
      {isDisabled && (
        <Alert
          type="warning"
          message={t('aiSearch.notEnabled')}
          showIcon
          style={{ marginBottom: 12 }}
        />
      )}

      {/* 一般エラー */}
      {parseMutation.isError && !isDisabled && (
        <Alert
          type="error"
          message={t('common.error')}
          showIcon
          style={{ marginBottom: 12 }}
        />
      )}

      {/* ローディング */}
      {parseMutation.isPending && (
        <div style={{ textAlign: 'center', padding: 24 }}>
          <Spin size="large" />
        </div>
      )}

      {/* 解析結果 */}
      {parseResult && !parseMutation.isPending && (
        <div
          style={{
            background: '#f8f9ff',
            border: '1px solid #d6e4ff',
            borderRadius: 8,
            padding: 16,
          }}
        >
          {/* サマリー */}
          {parseResult.summary && (
            <Alert
              type="info"
              message={
                <span>
                  <Text strong>{t('aiSearch.summaryLabel')}: </Text>
                  {parseResult.summary}
                </span>
              }
              style={{ marginBottom: 12 }}
            />
          )}

          <Text strong style={{ fontSize: 13 }}>
            {t('aiSearch.criteriaLabel')}
          </Text>

          {/* スキル条件 */}
          {parseResult.skill_matches.length > 0 && (
            <div style={{ marginTop: 8, marginBottom: 8 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {t('aiSearch.skillsLabel')}:{' '}
              </Text>
              <Space size={4} wrap style={{ marginTop: 4 }}>
                {parseResult.skill_matches.map(sm => (
                  <Tag
                    key={sm.skill_id}
                    color={sm.required ? 'blue' : 'green'}
                    style={{ fontSize: 12 }}
                  >
                    {sm.name}
                    {sm.level_min && (
                      <span style={{ opacity: 0.8, marginLeft: 4 }}>
                        {t('aiSearch.levelMin', { level: sm.level_min })}
                      </span>
                    )}
                    {' '}
                    <span style={{ opacity: 0.7, fontSize: 11 }}>
                      ({sm.required ? t('aiSearch.required') : t('aiSearch.optional')})
                    </span>
                  </Tag>
                ))}
              </Space>
            </div>
          )}

          {/* その他の条件 */}
          <div style={{ marginTop: 8, marginBottom: 8 }}>
            <Space size={4} wrap>
              {parseResult.criteria.japanese_level && (
                <Tag color="purple" style={{ fontSize: 12 }}>
                  {t('search.japaneseLevel')}: {t(`japaneseLevel.${parseResult.criteria.japanese_level}`)}
                </Tag>
              )}
              {parseResult.criteria.work_style && (
                <Tag style={{ fontSize: 12 }}>
                  {t(`workStyle.${parseResult.criteria.work_style}`)}
                </Tag>
              )}
              {parseResult.criteria.office_locations?.map(loc => (
                <Tag key={loc} style={{ fontSize: 12 }}>
                  {t(`officeLocation.${loc}`)}
                </Tag>
              ))}
              {parseResult.criteria.work_statuses?.map(ws => (
                <Tag key={ws} color="blue" style={{ fontSize: 12 }}>
                  {t(`workStatus.${ws}`)}
                </Tag>
              ))}
              {parseResult.criteria.free_from_before && (
                <Tag style={{ fontSize: 12 }}>
                  {t('search.freeFromBefore')}: {parseResult.criteria.free_from_before}
                </Tag>
              )}
            </Space>
          </div>

          {/* 条件なしメッセージ */}
          {parseResult.skill_matches.length === 0 &&
            !parseResult.criteria.japanese_level &&
            !parseResult.criteria.work_style &&
            (parseResult.criteria.office_locations?.length ?? 0) === 0 && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                {t('aiSearch.noConditions')}
              </Text>
            )}

          {/* マッチしなかった用語 */}
          {parseResult.unmatched_terms.length > 0 && (
            <Alert
              type="warning"
              icon={<WarningOutlined />}
              showIcon
              message={
                <span>
                  <Text strong style={{ fontSize: 12 }}>{t('aiSearch.unmatchedLabel')}: </Text>
                  {parseResult.unmatched_terms.map(term => (
                    <Tag key={term} style={{ fontSize: 11, marginLeft: 4 }}>
                      {term}
                    </Tag>
                  ))}
                </span>
              }
              style={{ marginTop: 10 }}
            />
          )}

          <Divider style={{ margin: '12px 0' }} />

          <Row gutter={8}>
            <Col>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleSearch}
              >
                {t('aiSearch.searchButton')}
              </Button>
            </Col>
            <Col>
              <Text type="secondary" style={{ fontSize: 12, lineHeight: '32px' }}>
                {t('aiSearch.editHint')}
              </Text>
            </Col>
          </Row>
        </div>
      )}
    </div>
  )
}
