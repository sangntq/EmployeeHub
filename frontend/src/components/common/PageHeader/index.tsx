import { Breadcrumb, Typography, Space } from 'antd'
import type { ReactNode } from 'react'

interface BreadcrumbItem {
  title: string
  href?: string
}

interface Props {
  title: string
  breadcrumbs?: BreadcrumbItem[]
  extra?: ReactNode    // 右側に表示するアクションボタン等
  subtitle?: string
}

export default function PageHeader({ title, breadcrumbs, extra, subtitle }: Props) {
  return (
    <div style={{ marginBottom: 24 }}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <Breadcrumb
          style={{ marginBottom: 8 }}
          items={breadcrumbs.map((item) => ({
            title: item.href ? <a href={item.href}>{item.title}</a> : item.title,
          }))}
        />
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <Typography.Title level={4} style={{ margin: 0 }}>
            {title}
          </Typography.Title>
          {subtitle && (
            <Typography.Text type="secondary" style={{ fontSize: 13 }}>
              {subtitle}
            </Typography.Text>
          )}
        </div>
        {extra && <Space>{extra}</Space>}
      </div>
    </div>
  )
}
