import type { AssetAnalysisResultResponse, AssetResponse } from '@/api/types'

interface AssetAnalysisResultProps {
  result: AssetAnalysisResultResponse
  asset?: AssetResponse
}

function formatPercentage(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}

function formatProbability(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${(parsedValue * 100).toFixed(2)} %`
}

function formatDecimal(value: string | null | undefined, maximumFractionDigits = 4): string {
  if (value === null || value === undefined) {
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

function formatDate(value: string): string {
  const date = new Date(`${value}T00:00:00`)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(date)
}

function formatTrend(trend: string): string {
  switch (trend.toUpperCase()) {
    case 'ALCISTA':
      return 'Alcista'
    case 'NEUTRAL':
      return 'Neutral'
    case 'BAJISTA':
      return 'Bajista'
    default:
      return trend
  }
}

export function AssetAnalysisResult({ result, asset }: AssetAnalysisResultProps) {
  const currency = asset?.currency ?? ''
  const assetTitle = asset ? `${asset.symbol} · ${asset.name}` : result.asset_id

  return (
    <section className="ai-result" aria-labelledby="ai-result-title">
      <header className="ai-result__header">
        <div>
          <p className="app__eyebrow">Predicción completada</p>
          <h2 id="ai-result-title">{assetTitle}</h2>
          <p>Resultado generado por los modelos de análisis registrados en AlphaInvest AI.</p>
        </div>

        <span className={`ai-trend ai-trend--${result.trend.toLowerCase()}`}>
          {formatTrend(result.trend)}
        </span>
      </header>

      <dl className="ai-result__metrics">
        <div>
          <dt>Fecha base</dt>
          <dd>{formatDate(result.base_date)}</dd>
        </div>

        <div>
          <dt>Fecha objetivo</dt>
          <dd>{formatDate(result.target_date)}</dd>
        </div>

        <div>
          <dt>Precio base</dt>
          <dd>
            {formatDecimal(result.base_price, 2)}
            {currency ? ` ${currency}` : ''}
          </dd>
        </div>

        <div>
          <dt>Precio estimado</dt>
          <dd>
            {formatDecimal(result.predicted_price, 2)}
            {currency ? ` ${currency}` : ''}
          </dd>
        </div>

        <div>
          <dt>Rendimiento esperado</dt>
          <dd>{formatPercentage(result.expected_return_percentage)}</dd>
        </div>

        <div>
          <dt>Confianza</dt>
          <dd>{formatProbability(result.confidence)}</dd>
        </div>
      </dl>

      <div className="ai-result__probabilities">
        <h3>Probabilidades de tendencia</h3>

        <dl className="ai-result__probability-grid">
          <div>
            <dt>Alcista</dt>
            <dd>{formatProbability(result.probabilities.bullish)}</dd>
          </div>

          <div>
            <dt>Neutral</dt>
            <dd>{formatProbability(result.probabilities.neutral)}</dd>
          </div>

          <div>
            <dt>Bajista</dt>
            <dd>{formatProbability(result.probabilities.bearish)}</dd>
          </div>
        </dl>
      </div>

      <p className="ai-result__notice">
        Esta información corresponde a un análisis estadístico del sistema y no constituye una
        garantía de rendimiento futuro.
      </p>
    </section>
  )
}
