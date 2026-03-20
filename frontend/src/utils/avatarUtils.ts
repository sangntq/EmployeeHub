/** アバターユーティリティ — 全画面で統一したアバタースタイルを提供する */

const AVATAR_COLORS = [
  '#4F46E5', '#7C3AED', '#DB2777', '#DC2626',
  '#D97706', '#059669', '#0891B2', '#2563EB',
]

/** 名前から一貫した背景色を返す（ハッシュベース） */
export function getAvatarColor(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
}

/** 名前からイニシャルを生成する */
export function getInitials(nameJa: string, nameEn: string | null | undefined): string {
  if (nameEn) {
    const parts = nameEn.trim().split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return nameEn.slice(0, 2).toUpperCase()
  }
  return (nameJa || '?').slice(0, 1)
}
