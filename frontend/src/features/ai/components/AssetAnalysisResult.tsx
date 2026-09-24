import type { AssetAnalysisResultResponse, AssetResponse } from '@/api/types'
import { ModelCardDetails } from '@/components/insights/ModelCardDetails'
import { ProbabilityBars } from '@/components/insights/ProbabilityBars'
import {
  describeTopProbability,
  formatProbabilityPercent,
  parseNumber,
  translateTrend,
} from '@/lib/aiInterpretation'
import { PRICE_FORECAST_MODEL_CARD, TREND_MODEL_CARD } from '@/lib/aiModelCards'

interface AssetAnalysisResultProps {
  result: AssetAnalysisResultResponse
  asset?: AssetResponse
}

/** Activo con el que se entrenaron los modelos de la versión actual. */
const TRAINING_SYMBOL = 'AAPL'

function formatPercentage(value: string | null | undefined): string {
  const parsed = parseNumber(value)

  if (parsed === null) {
    return 'No disponible'
  }

  return `${parsed > 0 ? '+' : ''}${parsed.toFixed(2)} %`
}

function formatDecimal(value: string | null | undefined, maximumFractionDigits = 4): string {
  const parsed = parseNumber(value)

  if (parsed === null) {
    return 'No disponible'
  }

  return new Intl.NumberFormat('es-MX', {
    maximumFractionDigits,
  }).format(parsed)
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

export function AssetAnalysisResult({ result, asset }: AssetAnalysisResultProps) {
  const currency = asset?.currency ?? ''
  const currencySuffix = currency ? ` ${currency}` : ''
  const assetTitle = asset ? `${asset.symbol} · ${asset.name}` : result.asset_id
  const trend = translateTrend(result.trend)
  const isTrainingAsset = asset?.symbol.toUpperCase() === TRAINING_SYMBOL

  return (
    <section className="ai-result" aria-labelledby="ai-result-title">
      <header className="ai-result__header">
        <div>
          <p className="app__eyebrow">Análisis completado</p>
          <h2 id="ai-result-title">{assetTitle}</h2>
        </div>

        <span className={`tone-badge tone-badge--${trend.tone}`}>{trend.text}</span>
      </header>

      <p className="insight-headline">
        Para las próximas 5 sesiones (del {formatDate(result.base_date)} al{' '}
        {formatDate(result.target_date)}), el modelo de tendencia se inclina por{' '}
        <strong>{trend.text.toLowerCase()}</strong> con{' '}
        {formatProbabilityPercent(result.confidence)} de probabilidad.
      </p>

      <p className="metric-hint">{describeTopProbability(result.confidence)}</p>

      {!isTrainingAsset ? (
        <div className="notice notice--warning" role="note">
          <strong>Modelo entrenado solo con {TRAINING_SYMBOL}</strong>
          <span>
            Los modelos de esta versión se entrenaron y evaluaron únicamente con datos de{' '}
            {TRAINING_SYMBOL}. Para {asset?.symbol ?? 'este activo'} el resultado es una referencia
            aún menos confiable.
          </span>
        </div>
      ) : null}

      <ProbabilityBars
        title="¿Hacia dónde se inclina el modelo?"
        items={[
          { label: 'Alcista', value: result.probabilities.bullish, tone: 'positive' },
          { label: 'Neutral', value: result.probabilities.neutral, tone: 'neutral' },
          { label: 'Bajista', value: result.probabilities.bearish, tone: 'negative' },
        ]}
      />

      <div className="notice" role="note">
        <strong>Precio de referencia a 5 sesiones</strong>
        <span>
          {formatDecimal(result.base_price, 2)}
          {currencySuffix} → {formatDecimal(result.predicted_price, 2)}
          {currencySuffix} ({formatPercentage(result.expected_return_percentage)}). Se obtiene
          aplicando al último precio el rendimiento mediano histórico; no es una predicción
          específica para esta fecha.
        </span>
      </div>

      <details className="technical-details">
        <summary>Detalle técnico</summary>

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
              {currencySuffix}
            </dd>
          </div>

          <div>
            <dt>Precio estimado</dt>
            <dd>
              {formatDecimal(result.predicted_price, 2)}
              {currencySuffix}
            </dd>
          </div>

          <div>
            <dt>Rendimiento esperado</dt>
            <dd>{formatPercentage(result.expected_return_percentage)}</dd>
          </div>

          <div>
            <dt>Confianza (probabilidad máxima)</dt>
            <dd>{formatDecimal(result.confidence, 4)}</dd>
          </div>

          <div>
            <dt>Probabilidad alcista</dt>
            <dd>{formatDecimal(result.probabilities.bullish, 4)}</dd>
          </div>

          <div>
            <dt>Probabilidad neutral</dt>
            <dd>{formatDecimal(result.probabilities.neutral, 4)}</dd>
          </div>

          <div>
            <dt>Probabilidad bajista</dt>
            <dd>{formatDecimal(result.probabilities.bearish, 4)}</dd>
          </div>
        </dl>
      </details>

      <ModelCardDetails card={TREND_MODEL_CARD} />
      <ModelCardDetails card={PRICE_FORECAST_MODEL_CARD} />

      <p className="ai-result__notice">
        Análisis estadístico con fines educativos. &quot;Alcista&quot; describe una inclinación del
        modelo, no una garantía de que el precio suba, ni una recomendación de inversión.
      </p>
    </section>
  )
}
