import type { AssetResponse, NewsResponse, SentimentAnalysisResultResponse } from '@/api/types'

interface SentimentAnalysisResultProps {
  result: SentimentAnalysisResultResponse
  asset?: AssetResponse
  news?: NewsResponse
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

function formatSentiment(sentiment: string): string {
  switch (sentiment.toUpperCase()) {
    case 'POSITIVO':
      return 'Positivo'
    case 'NEUTRAL':
      return 'Neutral'
    case 'NEGATIVO':
      return 'Negativo'
    default:
      return sentiment
  }
}

function sentimentClass(sentiment: string): string {
  switch (sentiment.toUpperCase()) {
    case 'POSITIVO':
      return 'positivo'
    case 'NEGATIVO':
      return 'negativo'
    default:
      return 'neutral'
  }
}

export function SentimentAnalysisResult({ result, asset, news }: SentimentAnalysisResultProps) {
  const assetTitle = asset
    ? `${asset.symbol} · ${asset.name}`
    : (result.asset_id ?? 'Activo no disponible')

  return (
    <section className="ai-result" aria-labelledby="ai-sentiment-result-title">
      <header className="ai-result__header">
        <div>
          <p className="app__eyebrow">Análisis de sentimiento completado</p>
          <h2 id="ai-sentiment-result-title">{assetTitle}</h2>
          <p>Resultado del análisis de lenguaje aplicado a la noticia seleccionada.</p>
        </div>

        <span className={`ai-trend ai-sentiment--${sentimentClass(result.sentiment)}`}>
          {formatSentiment(result.sentiment)}
        </span>
      </header>

      {news ? (
        <div className="ai-result__news">
          <strong>{news.title}</strong>
          <span>
            {news.source} · {formatDateTime(news.published_at)}
          </span>
        </div>
      ) : null}

      <dl className="ai-result__metrics">
        <div>
          <dt>Puntuación</dt>
          <dd>{formatDecimal(result.score)}</dd>
        </div>

        <div>
          <dt>Confianza</dt>
          <dd>{formatProbability(result.confidence)}</dd>
        </div>

        <div>
          <dt>Relevancia</dt>
          <dd>{formatProbability(result.relevance)}</dd>
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

      <div className="ai-result__probabilities">
        <h3>Probabilidades de sentimiento</h3>

        <dl className="ai-result__probability-grid">
          <div>
            <dt>Positivo</dt>
            <dd>{formatProbability(result.positive_probability)}</dd>
          </div>

          <div>
            <dt>Neutral</dt>
            <dd>{formatProbability(result.neutral_probability)}</dd>
          </div>

          <div>
            <dt>Negativo</dt>
            <dd>{formatProbability(result.negative_probability)}</dd>
          </div>
        </dl>
      </div>

      {result.summary ? (
        <div className="ai-result__summary">
          <h3>Resumen</h3>
          <p>{result.summary}</p>
        </div>
      ) : null}

      <p className="ai-result__notice">
        El sentimiento representa una clasificación automática del contenido analizado y no
        constituye por sí mismo una recomendación de inversión.
      </p>
    </section>
  )
}
