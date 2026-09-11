import type { ReactNode } from 'react'

import { PageState } from '@/components/PageState'

interface PageEmptyStateProps {
  title?: string
  description?: string
  action?: ReactNode
}

export function PageEmptyState({
  title = 'No hay información disponible',
  description,
  action,
}: PageEmptyStateProps) {
  return <PageState title={title} description={description} action={action} />
}
