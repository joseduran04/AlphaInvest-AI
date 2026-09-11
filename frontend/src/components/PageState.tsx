import type { ReactNode } from 'react'

interface PageStateProps {
  title: string
  description?: string
  action?: ReactNode
}

export function PageState({ title, description, action }: PageStateProps) {
  return (
    <section className="page-state" role="status">
      <div className="page-state__content">
        <h2>{title}</h2>

        {description ? <p>{description}</p> : null}

        {action ? <div className="page-state__action">{action}</div> : null}
      </div>
    </section>
  )
}
