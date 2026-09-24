import { useState } from 'react'

import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart'
import { PageLoadingState } from '@/components/PageLoadingState'
import { usePriceSeries } from '@/features/market/hooks/usePriceSeries'
import { getFinancialToneClass } from '@/lib/financialTone'
import { formatCurrency } from '@/lib/formatters'
import { PRICE_RANGES, type PriceRangeKey, rangeStartDate } from '@/lib/priceRanges'

interface AssetPriceChartProps {
  assetId: string
  symbol: string
}

/**
 * Gráfica de precio del activo al estilo de los portales financieros: una
 * línea de cierres diarios, verde si el periodo sube y roja si baja.
 * Lee los precios guardados en AlphaInvest (sin llamadas externas).
 */
export function AssetPriceChart({ assetId, symbol }: AssetPriceChartProps) {
  const [range, setRange] = useState<PriceRangeKey>('1A')
  // Ojo: 'Máx' usa months = null (todo el histórico), no un valor por defecto.
  const selectedRange = PRICE_RANGES.find((item) => item.key === range)
  const months = selectedRange ? selectedRange.months : 12

  const seriesQuery = usePriceSeries(assetId, rangeStartDate(months))
  const data = seriesQuery.data

  const change = data?.change === null || data?.change === undefined ? null : Number(data.change)
  const tone = change === null || change === 0 ? 'series-1' : change > 0 ? 'positive' : 'negative'

  return (
    <div className="asset-price-chart">
      <div className="asset-price-chart__toolbar">
        {data && data.last_close !== null ? (
          <div className="asset-price-chart__summary">
            <strong>{formatCurrency(data.last_close, data.currency)}</strong>
            {change !== null && data.change_percentage !== null ? (
              <span className={getFinancialToneClass(change)}>
                {`${change > 0 ? '+' : ''}${formatCurrency(change, data.currency)} (${change > 0 ? '+' : ''}${Number(data.change_percentage).toFixed(2)} %) en el periodo`}
              </span>
            ) : null}
          </div>
        ) : (
          <span />
        )}

        <div className="asset-price-chart__ranges" role="group" aria-label="Periodo de la gráfica">
          {PRICE_RANGES.map((item) => (
            <button
              key={item.key}
              type="button"
              className={`asset-price-chart__range${range === item.key ? ' asset-price-chart__range--active' : ''}`}
              aria-pressed={range === item.key}
              onClick={() => setRange(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {seriesQuery.isPending ? (
        <PageLoadingState message="Cargando gráfica de precios..." />
      ) : seriesQuery.isError ? (
        <p className="metric-hint" role="alert">
          No fue posible cargar la gráfica: {seriesQuery.error.message}
        </p>
      ) : data && data.points.length >= 2 ? (
        <div className={seriesQuery.isFetching ? 'asset-price-chart__plot--refreshing' : undefined}>
          <TimeSeriesChart
            title={`Precio de cierre de ${symbol}`}
            description={
              data.sampled
                ? 'Cierres diarios guardados en AlphaInvest AI (muestreados para el periodo largo).'
                : 'Cierres diarios guardados en AlphaInvest AI.'
            }
            dates={data.points.map((point) => point.date)}
            series={[
              {
                key: 'close',
                label: 'Cierre',
                color: tone,
                values: data.points.map((point) => Number(point.close)),
              },
            ]}
            formatValue={(value) => formatCurrency(value, data.currency)}
            height={300}
          />
        </div>
      ) : (
        <p className="metric-hint">
          No hay suficientes precios guardados en este periodo. Sincroniza los precios del activo
          para ver la gráfica.
        </p>
      )}
    </div>
  )
}
