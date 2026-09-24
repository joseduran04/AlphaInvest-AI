import { Link } from 'react-router'

import type { MarketMoverResponse } from '@/api/types'
import { DashboardPanelState } from '@/features/dashboard/components/DashboardPanelState'
import { useDashboardMarketMovers } from '@/features/dashboard/hooks/useDashboardMarketMovers'
import { formatDashboardMoney } from '@/features/dashboard/utils/dashboardFormatters'
import { getFinancialToneClass } from '@/lib/financialTone'

function formatSignedPercentage(value: string): string {
  const parsed = Number(value)

  if (!Number.isFinite(parsed)) {
    return value
  }

  return `${parsed > 0 ? '+' : ''}${parsed.toFixed(2)} %`
}

function formatSignedMoney(value: string, currency: string): string {
  const parsed = Number(value)
  const formatted = formatDashboardMoney(value, currency)

  return Number.isFinite(parsed) && parsed > 0 ? `+${formatted}` : formatted
}

function formatDate(value: string): string {
  const date = new Date(`${value}T00:00:00`)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium' }).format(date)
}

function MoversList({
  title,
  items,
  emptyMessage,
}: {
  title: string
  items: MarketMoverResponse[]
  emptyMessage: string
}) {
  return (
    <div className="market-movers__column">
      <h3>{title}</h3>

      {items.length === 0 ? (
        <p className="metric-hint">{emptyMessage}</p>
      ) : (
        <ol className="market-movers__list">
          {items.map((item) => (
            <li key={item.asset_id}>
              <Link className="market-movers__asset" to={`/app/market/assets/${item.asset_id}`}>
                <strong>{item.symbol}</strong>
                <span>{item.name}</span>
              </Link>

              <span className="market-movers__price">
                {formatDashboardMoney(item.last_close, item.currency)}
                <span className="metric-hint">{formatDate(item.last_date)}</span>
              </span>

              <span className={`market-movers__change ${getFinancialToneClass(item.change)}`}>
                <strong>{formatSignedPercentage(item.change_percentage)}</strong>
                <span>{formatSignedMoney(item.change, item.currency)}</span>
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}

/** Mayores alzas y bajas del catálogo de AlphaInvest en su última sesión. */
export function MarketMoversPanel() {
  const moversQuery = useDashboardMarketMovers()

  return (
    <article className="dashboard-panel dashboard-panel--wide">
      <header className="dashboard-panel__header">
        <div>
          <span className="dashboard-panel__eyebrow">Mercado</span>
          <h2>Mayores alzas y bajas</h2>
        </div>

        <Link className="dashboard-panel__link" to="/app/market">
          Ver mercado
        </Link>
      </header>

      {moversQuery.isPending ? (
        <DashboardPanelState message="Calculando movimientos del mercado..." />
      ) : moversQuery.isError ? (
        <DashboardPanelState
          error
          message={moversQuery.error.message}
          onRetry={() => {
            void moversQuery.refetch()
          }}
        />
      ) : (
        <>
          <div className="market-movers">
            <MoversList
              title="Top ganadores"
              items={moversQuery.data.gainers}
              emptyMessage="Ningún activo subió en su última sesión."
            />
            <MoversList
              title="Top perdedores"
              items={moversQuery.data.losers}
              emptyMessage="Ningún activo bajó en su última sesión."
            />
          </div>

          <p className="metric-hint">
            Variación entre los dos últimos cierres disponibles de los activos del catálogo de
            AlphaInvest AI. Los activos en pesos y en dólares se comparan por porcentaje.
          </p>
        </>
      )}
    </article>
  )
}
