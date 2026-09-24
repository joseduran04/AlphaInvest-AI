import type { AssetResponse, NewsResponse, SentimentAnalysisResultResponse } from '@/api/types'
import { ModelCardDetails } from '@/components/insights/ModelCardDetails'
import { ProbabilityBars } from '@/components/insights/ProbabilityBars'
import {
  describeRelevance,
  describeSentimentBalance,
  describeTopProbability,
  formatProbabilityPercent,
  parseNumber,
  translateSentiment,
} from '@/lib/aiInterpretation'
import { SENTIMENT_MODEL_CARD } from '@/lib/aiModelCards'

interface SentimentAnalysisResultProps {
  result: SentimentAnalysisResultResponse
  asset?: AssetResponse
  news?: NewsResponse
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

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function SentimentAnalysisResult({ result, asset, news }: SentimentAnalysisResultProps) {
  const assetTitle = asset
    ? `${asset.symbol} · ${asset.name}`
    : (result.asset_id ?? 'Activo no disponible')
  const sentiment = translateSentiment(result.sentiment)
  const balance = describeSentimentBalance({
    positive: result.positive_probability,
    negative: result.negative_probability,
  })
  const relevance = describeRelevance(result.relevance)

  return (
    <section className="ai-result" aria-labelledby="ai-sentiment-result-title">
      <header className="ai-result__header">
        <div>
          <p className="app__eyebrow">Análisis de sentimiento completado</p>
          <h2 id="ai-sentiment-result-title">{assetTitle}</h2>
        </div>

        <span className={`tone-badge tone-badge--${sentiment.tone}`}>{sentiment.text}</span>
      </header>

      {news ? (
        <div className="ai-result__news">
          <strong>{news.title}</strong>
          <span>
            {news.source} · {formatDateTime(news.published_at)}
          </span>
        </div>
      ) : null}

      <p className="insight-headline">
        El modelo lee esta noticia con <strong>{sentiment.text.toLowerCase()}</strong> (
        {formatProbabilityPercent(result.confidence)} de probabilidad).
        {relevance
          ? ` Según el proveedor, la noticia trata sobre ${asset?.symbol ?? 'el activo'} con una relevancia de ${relevance}.`
          : ''}
      </p>

      <p className="metric-hint">{describeTopProbability(result.confidence)}</p>

      <ProbabilityBars
        title="Tono detectado en el texto"
        items={[
          { label: 'Positivo', value: result.positive_probability, tone: 'positive' },
          { label: 'Neutral', value: result.neutral_probability, tone: 'neutral' },
          { label: 'Negativo', value: result.negative_probability, tone: 'negative' },
        ]}
      />

      {balance ? <p className="metric-hint">{balance}</p> : null}

      {result.summary ? (
        <div className="ai-result__summary">
          <h3>Resumen</h3>
          <p>{result.summary}</p>
        </div>
      ) : null}

      <details className="technical-details">
        <summary>Detalle técnico</summary>

        <dl className="ai-result__metrics">
          <div>
            <dt>Puntuación (P. positivo − P. negativo)</dt>
            <dd>{formatDecimal(result.score)}</dd>
          </div>

          <div>
            <dt>Confianza (probabilidad máxima)</dt>
            <dd>{formatDecimal(result.confidence)}</dd>
          </div>

          <div>
            <dt>Relevancia del proveedor (0 a 1)</dt>
            <dd>{formatDecimal(result.relevance)}</dd>
          </div>

          <div>
            <dt>Idioma</dt>
            <dd>{result.language ?? 'No disponible'}</dd>
          </div>

          <div>
            <dt>Tipo de fuente</dt>
            <dd>{result.source_type}</dd>
          </div>

          <div>
            <dt>Fecha del contenido</dt>
            <dd>{formatDateTime(result.content_date)}</dd>
          </div>
        </dl>
      </details>

      <ModelCardDetails card={SENTIMENT_MODEL_CARD} />

      <p className="ai-result__notice">
        El sentimiento describe el tono del texto, no el efecto que tendrá la noticia en el precio,
        y no constituye una recomendación de inversión.
      </p>
    </section>
  )
}
