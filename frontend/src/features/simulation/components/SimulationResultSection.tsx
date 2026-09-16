import { useMemo } from 'react'

import { ApiError } from '@/api/errors'
import type { AssetResponse, SimulationAssetResultResponse } from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAssets } from '@/features/market/hooks/useAssets'
import { useSimulationResult } from '@/features/simulation/hooks/useSimulationResult'
import { formatCurrency } from '@/lib/formatters'

interface SimulationResultSectionProps {
  executionId: string
  onClose: () => void
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

function formatNumber(value: string | null, maximumFractionDigits = 4): string {
  if (value === null) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return new Intl.NumberFormat('es-MX', {
    maximumFractionDigits,
  }).format(parsedValue)
}

function formatDate(value: unknown): string {
  if (typeof value !== 'string' || value.trim() === '') {
    return 'No disponible'
  }

  const date = new Date(`${value}T00:00:00`)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(date)
}

function getSummaryString(summary: Record<string, unknown> | null, key: string): string | null {
  const value = summary?.[key]

  return typeof value === 'string' ? value : null
}

function getResultErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 404) {
      return 'La ejecución solicitada ya no está disponible.'
    }

    if (error.status === 409) {
      return 'El resultado todavía no está disponible en el backend.'
    }

    if (error.status === 422) {
      return 'El backend rechazó la consulta del resultado.'
    }

    if (error.status >= 500) {
      return 'Ocurrió un problema en el servidor al consultar el resultado.'
    }
  }

  return error.message
}

function SimulationAssetResult({
  result,
  marketAsset,
  currency,
}: {
  result: SimulationAssetResultResponse
  marketAsset?: AssetResponse
  currency: string
}) {
  const assetTitle = marketAsset ? `${marketAsset.symbol} · ${marketAsset.name}` : result.activo_id

  const assetCurrency = marketAsset?.currency ?? currency

  const totalContributions = getSummaryString(result.detalle, 'aportaciones_totales')

  const finalQuantity = getSummaryString(result.detalle, 'cantidad_final')

  return (
    <article className="simulation-result-asset">
      <header className="simulation-result-asset__header">
        <div>
          <strong>{assetTitle}</strong>
          <span>
            {marketAsset
              ? `${marketAsset.asset_type.name} · ${marketAsset.market.name}`
              : 'Información de mercado no disponible'}
          </span>
        </div>

        <span>{formatPercentage(result.rendimiento_porcentaje)}</span>
      </header>

      <dl className="simulation-result-asset__grid">
        <div>
          <dt>Asignación</dt>
          <dd>{formatPercentage(result.porcentaje_asignado)}</dd>
        </div>

        <div>
          <dt>Capital asignado</dt>
          <dd>{formatCurrency(result.capital_asignado, currency)}</dd>
        </div>

        <div>
          <dt>Precio inicial</dt>
          <dd>{formatCurrency(result.precio_inicial, assetCurrency)}</dd>
        </div>

        <div>
          <dt>Precio final</dt>
          <dd>{formatCurrency(result.precio_final, assetCurrency)}</dd>
        </div>

        <div>
          <dt>Valor final</dt>
          <dd>{formatCurrency(result.valor_final, currency)}</dd>
        </div>

        <div>
          <dt>Ganancia / pérdida</dt>
          <dd>{formatCurrency(result.ganancia_perdida, currency)}</dd>
        </div>

        <div>
          <dt>Cantidad inicial</dt>
          <dd>{formatNumber(result.cantidad_inicial, 8)}</dd>
        </div>

        <div>
          <dt>Cantidad final</dt>
          <dd>{formatNumber(finalQuantity, 8)}</dd>
        </div>

        <div>
          <dt>Aportaciones</dt>
          <dd>
            {totalContributions === null
              ? 'No disponible'
              : formatCurrency(totalContributions, currency)}
          </dd>
        </div>

        <div>
          <dt>Volatilidad</dt>
          <dd>{formatPercentage(result.volatilidad)}</dd>
        </div>

        <div>
          <dt>Drawdown máximo</dt>
          <dd>{formatPercentage(result.maximo_drawdown_porcentaje)}</dd>
        </div>
      </dl>
    </article>
  )
}

export function SimulationResultSection({ executionId, onClose }: SimulationResultSectionProps) {
  const resultQuery = useSimulationResult(executionId)

  const marketAssetsQuery = useAssets({
    status: 'ACTIVO',
    limit: 100,
    offset: 0,
  })

  const marketAssetsById = useMemo(
    () => new Map((marketAssetsQuery.data?.items ?? []).map((asset) => [asset.id, asset])),
    [marketAssetsQuery.data?.items],
  )

  if (resultQuery.isPending) {
    return (
      <div className="simulation-result-panel">
        <PageLoadingState message="Cargando resultados de la simulación..." />
      </div>
    )
  }

  if (resultQuery.isError) {
    return (
      <div className="simulation-result-panel">
        <PageErrorState
          title="No fue posible cargar el resultado"
          message={getResultErrorMessage(resultQuery.error)}
          onRetry={() => {
            void resultQuery.refetch()
          }}
        />

        <button className="button button--secondary" type="button" onClick={onClose}>
          Cerrar resultados
        </button>
      </div>
    )
  }

  const result = resultQuery.data

  const effectiveStartDate = getSummaryString(result.resumen, 'fecha_inicio_efectiva')

  const effectiveEndDate = getSummaryString(result.resumen, 'fecha_fin_efectiva')

  const totalCommissions = getSummaryString(result.resumen, 'comisiones_totales')

  return (
    <div className="simulation-result-panel">
      <header className="simulation-result-panel__header">
        <div>
          <span className="simulation-results__eyebrow">Resultado histórico</span>
          <h3>Resumen de la ejecución</h3>
        </div>

        <button className="button button--secondary" type="button" onClick={onClose}>
          Cerrar resultados
        </button>
      </header>

      <dl className="simulation-result-summary">
        <div>
          <dt>Capital inicial</dt>
          <dd>{formatCurrency(result.capital_inicial, result.moneda)}</dd>
        </div>

        <div>
          <dt>Aportaciones totales</dt>
          <dd>{formatCurrency(result.aportaciones_totales, result.moneda)}</dd>
        </div>

        <div>
          <dt>Capital final</dt>
          <dd>{formatCurrency(result.capital_final, result.moneda)}</dd>
        </div>

        <div>
          <dt>Ganancia / pérdida</dt>
          <dd>{formatCurrency(result.ganancia_perdida, result.moneda)}</dd>
        </div>

        <div>
          <dt>Rendimiento total</dt>
          <dd>{formatPercentage(result.rendimiento_total_porcentaje)}</dd>
        </div>

        <div>
          <dt>Rendimiento anualizado</dt>
          <dd>{formatPercentage(result.rendimiento_anualizado_porcentaje)}</dd>
        </div>
      </dl>

      <div className="simulation-result-subsection">
        <h4>Riesgo y rendimiento</h4>

        <dl className="simulation-result-metrics">
          <div>
            <dt>Volatilidad anualizada</dt>
            <dd>{formatPercentage(result.volatilidad_anualizada)}</dd>
          </div>

          <div>
            <dt>Índice de Sharpe</dt>
            <dd>{formatNumber(result.indice_sharpe)}</dd>
          </div>

          <div>
            <dt>Drawdown máximo</dt>
            <dd>{formatPercentage(result.maximo_drawdown_porcentaje)}</dd>
          </div>

          <div>
            <dt>Valor en riesgo (VaR)</dt>
            <dd>
              {result.valor_en_riesgo === null
                ? 'No disponible'
                : formatCurrency(result.valor_en_riesgo, result.moneda)}
            </dd>
          </div>

          <div>
            <dt>Nivel de confianza VaR</dt>
            <dd>
              {result.nivel_confianza_var === null
                ? 'No disponible'
                : formatPercentage(String(Number(result.nivel_confianza_var) * 100))}
            </dd>
          </div>
        </dl>
      </div>

      <div className="simulation-result-subsection">
        <h4>Periodo efectivo</h4>

        <dl className="simulation-result-metrics">
          <div>
            <dt>Inicio efectivo</dt>
            <dd>{formatDate(effectiveStartDate)}</dd>
          </div>

          <div>
            <dt>Fin efectivo</dt>
            <dd>{formatDate(effectiveEndDate)}</dd>
          </div>

          <div>
            <dt>Comisiones totales</dt>
            <dd>
              {totalCommissions === null
                ? 'No disponible'
                : formatCurrency(totalCommissions, result.moneda)}
            </dd>
          </div>
        </dl>
      </div>

      <div className="simulation-result-subsection">
        <h4>Resultados por activo</h4>

        {result.activos.length === 0 ? (
          <p>No existen resultados por activo registrados.</p>
        ) : (
          <div className="simulation-result-assets">
            {result.activos.map((assetResult) => (
              <SimulationAssetResult
                key={assetResult.id}
                result={assetResult}
                marketAsset={marketAssetsById.get(assetResult.activo_id)}
                currency={result.moneda}
              />
            ))}
          </div>
        )}

        {marketAssetsQuery.isError ? (
          <p className="simulation-result-market-warning">
            No fue posible cargar el catálogo de mercado. Los activos sin información disponible se
            identificarán mediante su ID.
          </p>
        ) : null}
      </div>
    </div>
  )
}
