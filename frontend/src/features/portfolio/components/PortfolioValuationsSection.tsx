import { ApiError } from '@/api/errors'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useCreatePortfolioValuation } from '@/features/portfolio/hooks/useCreatePortfolioValuation'
import { usePortfolioValuations } from '@/features/portfolio/hooks/usePortfolioValuations'
import { getFinancialToneClass } from '@/lib/financialTone'
import { formatCurrency } from '@/lib/formatters'

interface PortfolioValuationsSectionProps {
  portfolioId: string
  canCreate: boolean
}

function formatDateTime(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function formatPercentage(value: string | null): string {
  if (value === null) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}

function getCreateErrorMessage(error: Error): string {
  if (!(error instanceof ApiError)) {
    return error.message
  }

  switch (error.status) {
    case 400:
      return 'No fue posible registrar la valoración con el estado actual del portafolio.'
    case 403:
      return 'No tienes permisos para registrar una valoración.'
    case 404:
      return 'El portafolio ya no está disponible.'
    case 409:
      return 'No fue posible registrar la valoración por un conflicto con el estado actual del portafolio.'
    case 422:
      return 'El backend rechazó los datos utilizados para registrar la valoración.'
    default:
      return error.message
  }
}

export function PortfolioValuationsSection({
  portfolioId,
  canCreate,
}: PortfolioValuationsSectionProps) {
  const valuationsQuery = usePortfolioValuations(portfolioId)

  const createValuationMutation = useCreatePortfolioValuation(portfolioId)

  const handleCreateValuation = () => {
    createValuationMutation.mutate({})
  }

  return (
    <section className="portfolio-detail-section">
      <header className="portfolio-detail-section__header">
        <div>
          <p className="portfolio-results__eyebrow">Histórico</p>
          <h2>Valoraciones del portafolio</h2>
        </div>

        {canCreate ? (
          <button
            className="button button--primary"
            type="button"
            disabled={createValuationMutation.isPending}
            onClick={handleCreateValuation}
          >
            {createValuationMutation.isPending ? 'Registrando...' : 'Registrar valoración actual'}
          </button>
        ) : null}
      </header>

      <p className="portfolio-valuations__description">
        Guarda una fotografía de las métricas financieras actuales para consultar posteriormente la
        evolución del portafolio.
      </p>

      {createValuationMutation.isSuccess ? (
        <p className="portfolio-valuations__feedback" role="status">
          La valoración fue registrada correctamente.
        </p>
      ) : null}

      {createValuationMutation.isError ? (
        <p
          className="portfolio-valuations__feedback portfolio-valuations__feedback--error"
          role="alert"
        >
          {getCreateErrorMessage(createValuationMutation.error)}
        </p>
      ) : null}

      {valuationsQuery.isPending ? (
        <PageLoadingState message="Cargando historial de valoraciones..." />
      ) : valuationsQuery.isError ? (
        <PageErrorState
          title="No fue posible cargar las valoraciones"
          message={valuationsQuery.error.message}
          onRetry={() => {
            void valuationsQuery.refetch()
          }}
        />
      ) : valuationsQuery.data.items.length === 0 ? (
        <p className="portfolio-detail-section__empty">
          Todavía no existen valoraciones históricas registradas para este portafolio.
        </p>
      ) : (
        <>
          <div className="portfolio-valuations__summary">
            <span>
              {valuationsQuery.data.total}{' '}
              {valuationsQuery.data.total === 1
                ? 'valoración registrada'
                : 'valoraciones registradas'}
            </span>
          </div>

          <div className="portfolio-valuations-list">
            {valuationsQuery.data.items.map((valuation) => (
              <article key={valuation.id} className="portfolio-valuation-card">
                <header className="portfolio-valuation-card__header">
                  <div>
                    <strong>{formatCurrency(valuation.valor_posiciones, valuation.moneda)}</strong>

                    <span>{formatDateTime(valuation.fecha_hora)}</span>
                  </div>

                  <span
                    className={`portfolio-valuation-card__return ${getFinancialToneClass(valuation.rendimiento_porcentaje)}`}
                  >
                    {formatPercentage(valuation.rendimiento_porcentaje)}
                  </span>
                </header>

                <dl className="portfolio-valuation-card__metrics">
                  <div>
                    <dt>Valor actual</dt>
                    <dd>{formatCurrency(valuation.valor_posiciones, valuation.moneda)}</dd>
                  </div>

                  <div>
                    <dt>Capital invertido</dt>
                    <dd>{formatCurrency(valuation.capital_invertido, valuation.moneda)}</dd>
                  </div>

                  <div>
                    <dt>Ganancia / pérdida</dt>
                    <dd className={getFinancialToneClass(valuation.ganancia_perdida)}>
                      {formatCurrency(valuation.ganancia_perdida, valuation.moneda)}
                    </dd>
                  </div>
                </dl>

                <footer className="portfolio-valuation-card__footer">
                  <span>Registrada {formatDateTime(valuation.fecha_registro)}</span>
                </footer>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  )
}
