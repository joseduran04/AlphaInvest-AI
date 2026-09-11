interface PageErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
}

export function PageErrorState({
  title = 'No fue posible cargar la información',
  message = 'Ocurrió un problema al procesar la solicitud.',
  onRetry,
}: PageErrorStateProps) {
  return (
    <section className="page-state page-state--error" role="alert">
      <div className="page-state__content">
        <h2>{title}</h2>
        <p>{message}</p>

        {onRetry ? (
          <div className="page-state__action">
            <button className="button button--secondary" type="button" onClick={onRetry}>
              Reintentar
            </button>
          </div>
        ) : null}
      </div>
    </section>
  )
}
