import { Empty, Button } from 'antd'
import type { ReactNode } from 'react'

interface Props {
  description?: string
  ctaLabel?: string
  onCta?: () => void
  icon?: ReactNode
}

export default function EmptyState({ description, ctaLabel, onCta, icon }: Props) {
  return (
    <Empty
      image={icon ?? Empty.PRESENTED_IMAGE_SIMPLE}
      description={description}
      style={{ padding: '48px 0' }}
    >
      {ctaLabel && onCta && (
        <Button type="primary" onClick={onCta}>
          {ctaLabel}
        </Button>
      )}
    </Empty>
  )
}
