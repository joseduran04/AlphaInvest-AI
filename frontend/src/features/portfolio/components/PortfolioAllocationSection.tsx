import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { usePortfolioAssetAllocation } from '@/features/portfolio/hooks/usePortfolioAssetAllocation'
import { usePortfolioSectorAllocation } from '@/features/portfolio/hooks/usePortfolioSectorAllocation'
import { formatCurrency } from '@/lib/formatters'

interface PortfolioAllocationSectionProps {
  portfolioId: string
}

function formatPercentage(value: string): string {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}

function formatQuantity(value: string): string {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return new Intl.NumberFormat('es-MX', {
    maximumFractionDigits: 8,
  }).format(parsedValue)
}

function getPercentageWidth(value: string): number {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return 0
  }

  return Math.min(100, Math.max(0, parsedValue))
}

export function PortfolioAllocationSection({ portfolioId }: PortfolioAllocationSectionProps) {
  const assetAllocationQuery = usePortfolioAssetAllocation(portfolioId)
  const sectorAllocationQuery = usePortfolioSectorAllocation(portfolioId)

  return (
    <section className="portfolio-detail-section">
      <header className="portfolio-detail-section__header">
        <div>
          <p className="portfolio-results__eyebrow">Distribución</p>
          <h2>Composición del portafolio</h2>
        </div>
      </header>

      <div className="portfolio-allocation-grid">
        <section
          className="portfolio-allocation-panel"
          aria-labelledby="portfolio-asset-allocation-title"
        >
          <header className="portfolio-allocation-panel__header">
            <div>
              <h3 id="portfolio-asset-allocation-title">Por activo</h3>
              <p>Distribución del valor de las posiciones entre los activos.</p>
            </div>

            {assetAllocationQuery.data ? (
              <div className="portfolio-allocation-total">
                <span>Valor distribuido</span>
                <strong>
                  {formatCurrency(
                    assetAllocationQuery.data.valor_total_distribuido,
                    assetAllocationQuery.data.moneda_base,
                  )}
                </strong>
              </div>
            ) : null}
          </header>

          {assetAllocationQuery.isPending ? (
            <PageLoadingState message="Cargando distribución por activo..." />
          ) : assetAllocationQuery.isError ? (
            <PageErrorState
              title="No fue posible cargar la distribución por activo"
              message={assetAllocationQuery.error.message}
              onRetry={() => {
                void assetAllocationQuery.refetch()
              }}
            />
          ) : assetAllocationQuery.data.items.length === 0 ? (
            <p className="portfolio-detail-section__empty">
              No existen posiciones para calcular la distribución por activo.
            </p>
          ) : (
            <div className="portfolio-allocation-list">
              {assetAllocationQuery.data.items.map((item) => {
                const percentageWidth = getPercentageWidth(item.porcentaje)

                return (
                  <article key={item.activo_id} className="portfolio-allocation-item">
                    <div className="portfolio-allocation-item__header">
                      <div>
                        <strong>{item.simbolo}</strong>
                        <span>{item.nombre}</span>
                      </div>

                      <strong>{formatPercentage(item.porcentaje)}</strong>
                    </div>

                    <div
                      className="portfolio-allocation-bar"
                      role="progressbar"
                      aria-label={`Distribución de ${item.simbolo}`}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={percentageWidth}
                    >
                      <span style={{ width: `${percentageWidth}%` }} />
                    </div>

                    <dl className="portfolio-allocation-item__details">
                      <div>
                        <dt>Cantidad</dt>
                        <dd>{formatQuantity(item.cantidad)}</dd>
                      </div>

                      <div>
                        <dt>Valor de referencia</dt>
                        <dd>
                          {formatCurrency(
                            item.valor_referencia,
                            assetAllocationQuery.data.moneda_base,
                          )}
                        </dd>
                      </div>

                      <div>
                        <dt>Sector</dt>
                        <dd>{item.sector ?? 'Sin sector registrado'}</dd>
                      </div>

                      <div>
                        <dt>Industria</dt>
                        <dd>{item.industria ?? 'Sin industria registrada'}</dd>
                      </div>
                    </dl>
                  </article>
                )
              })}
            </div>
          )}
        </section>

        <section
          className="portfolio-allocation-panel"
          aria-labelledby="portfolio-sector-allocation-title"
        >
          <header className="portfolio-allocation-panel__header">
            <div>
              <h3 id="portfolio-sector-allocation-title">Por sector</h3>
              <p>Agrupación del valor de las posiciones según su sector.</p>
            </div>

            {sectorAllocationQuery.data ? (
              <div className="portfolio-allocation-total">
                <span>Valor distribuido</span>
                <strong>
                  {formatCurrency(
                    sectorAllocationQuery.data.valor_total_distribuido,
                    sectorAllocationQuery.data.moneda_base,
                  )}
                </strong>
              </div>
            ) : null}
          </header>

          {sectorAllocationQuery.isPending ? (
            <PageLoadingState message="Cargando distribución por sector..." />
          ) : sectorAllocationQuery.isError ? (
            <PageErrorState
              title="No fue posible cargar la distribución por sector"
              message={sectorAllocationQuery.error.message}
              onRetry={() => {
                void sectorAllocationQuery.refetch()
              }}
            />
          ) : sectorAllocationQuery.data.items.length === 0 ? (
            <p className="portfolio-detail-section__empty">
              No existen posiciones para calcular la distribución por sector.
            </p>
          ) : (
            <div className="portfolio-allocation-list">
              {sectorAllocationQuery.data.items.map((item) => {
                const percentageWidth = getPercentageWidth(item.porcentaje)

                return (
                  <article key={item.sector} className="portfolio-allocation-item">
                    <div className="portfolio-allocation-item__header">
                      <div>
                        <strong>{item.sector}</strong>
                        <span>
                          {item.posiciones} {item.posiciones === 1 ? 'posición' : 'posiciones'}
                        </span>
                      </div>

                      <strong>{formatPercentage(item.porcentaje)}</strong>
                    </div>

                    <div
                      className="portfolio-allocation-bar"
                      role="progressbar"
                      aria-label={`Distribución del sector ${item.sector}`}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={percentageWidth}
                    >
                      <span style={{ width: `${percentageWidth}%` }} />
                    </div>

                    <dl className="portfolio-allocation-item__details portfolio-allocation-item__details--sector">
                      <div>
                        <dt>Posiciones</dt>
                        <dd>{item.posiciones}</dd>
                      </div>

                      <div>
                        <dt>Valor de referencia</dt>
                        <dd>
                          {formatCurrency(
                            item.valor_referencia,
                            sectorAllocationQuery.data.moneda_base,
                          )}
                        </dd>
                      </div>
                    </dl>
                  </article>
                )
              })}
            </div>
          )}
        </section>
      </div>
    </section>
  )
}
