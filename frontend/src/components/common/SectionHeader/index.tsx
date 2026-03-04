/**
 * SectionHeader — セクション区切りヘッダー
 *
 * カテゴリ別グループ（資格管理・スキルマトリクス等）の視覚的な区切りに使用する。
 * accentColor でカテゴリ固有のカラーリングを指定できる。
 *
 * 使用例:
 *   <SectionHeader
 *     title="クラウド"
 *     icon="☁️"
 *     accentColor="#0EA5E9"
 *     tags={["44 種類", "465 名"]}
 *   />
 */
import { Tag } from 'antd'
import type { CSSProperties, ReactNode } from 'react'

interface SectionHeaderProps {
  title: string
  /** 絵文字または ReactNode（左側アイコン） */
  icon?: ReactNode
  /** 左ボーダー・背景ティントの色（デフォルト: indigo） */
  accentColor?: string
  /** 右側に表示するタグテキスト一覧 */
  tags?: string[]
  style?: CSSProperties
}

export default function SectionHeader({
  title,
  icon,
  accentColor = '#4F46E5',
  tags,
  style,
}: SectionHeaderProps) {
  // accentColor を HEX として透明度バリアントを生成
  const bgColor = `${accentColor}12`       // ~7% opacity
  const tagBg   = `${accentColor}18`       // ~10% opacity
  const tagBorder = `${accentColor}40`     // ~25% opacity

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '9px 14px',
        background: bgColor,
        borderLeft: `3px solid ${accentColor}`,
        borderRadius: '0 8px 8px 0',
        marginBottom: 14,
        ...style,
      }}
    >
      {/* 絵文字 / アイコン */}
      {icon != null && (
        <span
          style={{
            fontSize: 17,
            lineHeight: 1,
            display: 'flex',
            alignItems: 'center',
            flexShrink: 0,
          }}
        >
          {icon}
        </span>
      )}

      {/* タイトル */}
      <span
        style={{
          fontSize: 13,
          fontWeight: 700,
          color: '#111827',
          letterSpacing: '-0.01em',
          flex: 1,
        }}
      >
        {title}
      </span>

      {/* メタタグ群（右側） */}
      {tags?.map((tag) => (
        <Tag
          key={tag}
          style={{
            background: tagBg,
            border: `1px solid ${tagBorder}`,
            color: accentColor,
            fontWeight: 600,
            fontSize: 11,
            marginRight: 0,
            lineHeight: '18px',
          }}
        >
          {tag}
        </Tag>
      ))}
    </div>
  )
}
