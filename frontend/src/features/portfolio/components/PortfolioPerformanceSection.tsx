import { useMemo } from 'react'

import type { AssetResponse, PositionResponse } from '@/api/types'
import { GroupedBarChart } from '@/components/charts/GroupedBarChart'
import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useDailyCloses } from '@/features/market/hooks/useDailyCloses'
import { formatCurrency } from '@/lib/formatters'
import { benchmarkReturn, buildPortfolioSeries } from '@/lib/performanceSeries'

interface PortfolioPerformanceSectionProps {
  positions: PositionResponse[]
  assetsById: Map<string, AssetResponse>
  benchmarkAsset?: AssetResponse
  currency: string
}

function formatPercentage(value: number): string {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)} %`
}

/**
 * Gráficas del portafolio: evolución de lo invertido contra su valor,
 * rendimiento comparado con el S&P 500 (SPY) y ganancia/pérdida por posición.
 */
export function PortfolioPerformanceSection({
  positions,
  assetsById,
  benchmarkAsset,
  currency,
}: PortfolioPerformanceSectionProps) {
  const openPositions = useMemo(
    () => positions.filter((position) => position.estado === 'ABIERTA'),
    [positions],
  )

  const startDate = useMemo(() => {
    const dates = openPositions.map((position) => position.fecha_apertura.slice(0, 10)).sort()

    return dates[0] ?? null
  }, [openPositions])

  const assetIds = useMemo(() => {
    const ids = new Set(openPositions.map((position) => position.activo_id))

    if (benchmarkAsset) {
      ids.add(benchmarkAsset.id)
    }

    return [...ids]
  }, [benchmarkAsset, openPositions])

  const { closesByAsset, isPending, isError, errorMessage } = useDailyCloses(assetIds, startDate)

  const series = useMemo(
    () =>
      buildPortfolioSeries(
        openPositions.map((position) => ({
          assetId: position.activo_id,
          quantity: Number(position.cantidad),
          cost: Number(position.costo_total),
          openedOn: position.fecha_apertura.slice(0, 10),
        })),
        new Map(
          [...closesByAsset.entries()].filter(([assetId]) =>
            openPositions.some((position) => position.activo_id === assetId),
          ),
        ),
      ),
    [closesByAsset, openPositions],
  )

  const benchmarkCloses = benchmarkAsset ? closesByAsset.get(benchmarkAsset.id) : undefined

  const barItems = openPositions
    .filter((position) => position.valor_actual !== null)
    .map((position) => {
      const before = Number(position.costo_total)
      const after = Number(position.valor_actual)
      const change = after - before
      const percentage = before > 0 ? (change / before) * 100 : 0

      return {
        key: position.id,
        label: assetsById.get(position.activo_id)?.symbol ?? 'Activo',
        before,
        after,
        changeLabel: `${change > 0 ? '+' : ''}${formatCurrency(change, currency)} · ${formatPercentage(percentage)}`,
      }
    })
    .sort((a, b) => b.after - b.before - (a.after - a.before))

  if (openPositions.length === 0) {
    return null
  }

  return (
    <section className="portfolio-detail-section">
      <header className="portfolio-detail-section__header">
        <div>
          <p className="portfolio-results__eyebrow">Gráficas</p>
          <h2>Desempeño del portafolio</h2>
        </div>
      </header>

      <div className="portfolio-charts">
        {isPending ? (
          <PageLoadingState message="Cargando precios históricos..." />
        ) : isError ? (
          <p className="metric-hint" role="alert">
            No fue posible cargar los precios históricos: {errorMessage}
          </p>
        ) : series.dates.length < 2 ? (
          <p className="metric-hint">
            Aún no hay suficientes precios desde la apertura de las posiciones para graficar su
            evolución.
          </p>
        ) : (
          <>
            <TimeSeriesChart
              title="Lo invertido contra su valor actual"
              description="Valor diario de las posiciones abiertas desde su fecha de apertura, con su cantidad actual."
              dates={series.dates}
              series={[
                {
                  key: 'value',
                  label: 'Valor de las posiciones',
                  color: 'series-1',
                  values: series.value,
                },
                {
                  key: 'invested',
                  label: 'Capital invertido',
                  color: 'series-2',
                  dashed: true,
                  values: series.invested,
                },
              ]}
              formatValue={(value) => formatCurrency(value, currency)}
            />

            {benchmarkAsset && benchmarkCloses ? (
              <TimeSeriesChart
                title="Tu rendimiento contra el S&P 500"
                description={`Rendimiento acumulado desde ${series.dates[0]}. ${benchmarkAsset.symbol} es un ETF que replica el índice S&P 500.`}
                dates={series.dates}
                referenceValue={0}
                series={[
                  {
                    key: 'portfolio',
                    label: 'Tu portafolio',
                    color: 'series-1',
                    values: series.returnPercentage,
                  },
                  {
                    key: 'benchmark',
                    label: `S&P 500 (${benchmarkAsset.symbol})`,
                    color: 'series-2',
                    values: benchmarkReturn(series.dates, benchmarkCloses),
                  },
                ]}
                formatValue={formatPercentage}
              />
            ) : null}
          </>
        )}

        {barItems.length > 0 ? (
          <GroupedBarChart
            title="Antes y después por activo"
            description="Lo que invertiste en cada posición contra lo que vale hoy. Arriba, la ganancia o pérdida."
            beforeLabel="Invertido (antes)"
            afterLabel="Valor actual (después)"
            items={barItems}
            formatValue={(value) => formatCurrency(value, currency)}
          />
        ) : null}
      </div>
    </section>
  )
}
