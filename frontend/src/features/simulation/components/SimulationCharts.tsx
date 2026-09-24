import { useMemo } from 'react'

import type { AssetResponse, SimulationResultResponse } from '@/api/types'
import { GroupedBarChart } from '@/components/charts/GroupedBarChart'
import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart'
import { useDailyCloses } from '@/features/market/hooks/useDailyCloses'
import { formatCurrency } from '@/lib/formatters'
import { benchmarkReturn } from '@/lib/performanceSeries'

interface EvolutionPoint {
  fecha: string
  valor: string
  aportado: string
}

interface SimulationChartsProps {
  result: SimulationResultResponse
  marketAssetsById: Map<string, AssetResponse>
  benchmarkAsset?: AssetResponse
}

function readEvolution(summary: Record<string, unknown> | null): EvolutionPoint[] {
  const raw = summary?.evolucion

  if (!Array.isArray(raw)) {
    return []
  }

  return raw.filter(
    (point): point is EvolutionPoint =>
      typeof point === 'object' &&
      point !== null &&
      typeof (point as EvolutionPoint).fecha === 'string' &&
      typeof (point as EvolutionPoint).valor === 'string' &&
      typeof (point as EvolutionPoint).aportado === 'string',
  )
}

function formatPercentage(value: number): string {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)} %`
}

/**
 * Gráficas de una simulación: valor del portafolio contra capital aportado,
 * rendimiento contra el S&P 500 y resultado por activo.
 */
export function SimulationCharts({
  result,
  marketAssetsById,
  benchmarkAsset,
}: SimulationChartsProps) {
  const evolution = useMemo(() => readEvolution(result.resumen), [result.resumen])

  const dates = useMemo(() => evolution.map((point) => point.fecha), [evolution])
  const startDate = dates[0] ?? null
  const endDate = dates.at(-1)

  const { closesByAsset } = useDailyCloses(
    benchmarkAsset && startDate ? [benchmarkAsset.id] : [],
    startDate,
    endDate,
  )

  const benchmarkCloses = benchmarkAsset ? closesByAsset.get(benchmarkAsset.id) : undefined

  const assetBars = result.activos
    .map((assetResult) => {
      const change = Number(assetResult.ganancia_perdida)

      return {
        key: assetResult.id,
        label: marketAssetsById.get(assetResult.activo_id)?.symbol ?? 'Activo',
        before: Number(assetResult.capital_asignado),
        after: Number(assetResult.valor_final),
        changeLabel: `${change > 0 ? '+' : ''}${formatCurrency(change, result.moneda)} · ${formatPercentage(Number(assetResult.rendimiento_porcentaje))}`,
      }
    })
    .filter((item) => Number.isFinite(item.before) && Number.isFinite(item.after))
    .sort((a, b) => b.after - b.before - (a.after - a.before))

  const simulationReturn = evolution.map((point) => {
    const value = Number(point.valor)
    const contributed = Number(point.aportado)

    return contributed > 0 ? (value / contributed - 1) * 100 : null
  })

  return (
    <div className="simulation-result-subsection simulation-charts">
      <h4>Gráficas</h4>

      {evolution.length < 2 ? (
        <p className="metric-hint">
          Esta ejecución no guardó su evolución diaria. Vuelve a ejecutar la simulación para ver la
          gráfica del periodo.
        </p>
      ) : (
        <>
          <TimeSeriesChart
            title="Valor del portafolio contra capital aportado"
            description="Valor diario de la simulación. El capital aportado incluye el capital inicial y las aportaciones periódicas."
            dates={dates}
            series={[
              {
                key: 'value',
                label: 'Valor del portafolio',
                color: 'series-1',
                values: evolution.map((point) => Number(point.valor)),
              },
              {
                key: 'contributed',
                label: 'Capital aportado',
                color: 'series-2',
                dashed: true,
                values: evolution.map((point) => Number(point.aportado)),
              },
            ]}
            formatValue={(value) => formatCurrency(value, result.moneda)}
          />

          {benchmarkAsset && benchmarkCloses && benchmarkCloses.size > 0 ? (
            <TimeSeriesChart
              title="Rendimiento contra el S&P 500"
              description={`Rendimiento acumulado en el mismo periodo. ${benchmarkAsset.symbol} es un ETF que replica el índice S&P 500.`}
              dates={dates}
              referenceValue={0}
              series={[
                {
                  key: 'simulation',
                  label: 'Tu simulación',
                  color: 'series-1',
                  values: simulationReturn,
                },
                {
                  key: 'benchmark',
                  label: `S&P 500 (${benchmarkAsset.symbol})`,
                  color: 'series-2',
                  values: benchmarkReturn(dates, benchmarkCloses),
                },
              ]}
              formatValue={formatPercentage}
            />
          ) : null}
        </>
      )}

      {assetBars.length > 0 ? (
        <GroupedBarChart
          title="Antes y después por activo"
          description="Capital asignado a cada activo al inicio contra su valor al final del periodo. Arriba, la ganancia o pérdida."
          beforeLabel="Capital asignado (antes)"
          afterLabel="Valor final (después)"
          items={assetBars}
          formatValue={(value) => formatCurrency(value, result.moneda)}
        />
      ) : null}
    </div>
  )
}
