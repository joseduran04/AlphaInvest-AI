interface DashboardPanelStateProps {
  message: string
  error?: boolean
  onRetry?: () => void
}

export function DashboardPanelState({ message, error = false, onRetry }: DashboardPanelStateProps) {
  return (
    <div
      className={`dashboard-panel-state${error ? ' dashboard-panel-state--error' : ''}`}
      role={error ? 'alert' : 'status'}
    >
      <p>{message}</p>

      {onRetry ? (
        <button className="button button--secondary" type="button" onClick={onRetry}>
          Reintentar
        </button>
      ) : null}
    </div>
  )
}
