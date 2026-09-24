import type { AssetResponse } from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAssetSentimentSummary } from '@/features/ai/hooks/useAssetSentimentSummary'
import { translateSentiment } from '@/lib/aiInterpretation'

interface AssetSentimentThermometerProps {
  asset: AssetResponse
}

function formatDate(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium' }).format(date)
}

function percent(part: number, total: number): number {
  return total === 0 ? 0 : Math.round((part / total) * 100)
}

/**
 * Termómetro de sentimiento: cuántas de las noticias analizadas del activo
 * tuvieron tono positivo, neutral o negativo. Describe el tono; no predice
 * el precio.
 */
export function AssetSentimentThermometer({ asset }: AssetSentimentThermometerProps) {
  const summaryQuery = useAssetSentimentSummary(asset.id)

  return (
    <section className="ai-thermometer" aria-labelledby="ai-thermometer-title">
      <header>
        <p className="app__eyebrow">Termómetro de sentimiento</p>
        <h2 id="ai-thermometer-title">{asset.symbol} en las noticias</h2>
      </header>

      {summaryQuery.isPending ? (
        <PageLoadingState message="Cargando noticias analizadas..." />
      ) : summaryQuery.isError ? (
        <PageErrorState
          title="No fue posible cargar el termómetro"
          message={summaryQuery.error.message}
          onRetry={() => {
            void summaryQuery.refetch()
          }}
        />
      ) : summaryQuery.data.analyzed_news === 0 ? (
        <p className="metric-hint">
          Todavía no hay noticias analizadas de {asset.symbol}. Analiza una noticia para empezar.
        </p>
      ) : (
        <>
          <p className="insight-headline">
            De las últimas {summaryQuery.data.analyzed_news} noticias analizadas de {asset.symbol}:{' '}
            <strong className="financial-value financial-value--positive">
              {summaryQuery.data.positive} positivas
            </strong>
            , {summaryQuery.data.neutral} neutrales y{' '}
            <strong className="financial-value financial-value--negative">
              {summaryQuery.data.negative} negativas
            </strong>
            .
          </p>

          <div
            className="ai-thermometer__bar"
            role="img"
            aria-label={`${summaryQuery.data.positive} positivas, ${summaryQuery.data.neutral} neutrales, ${summaryQuery.data.negative} negativas`}
          >
            <span
              className="ai-thermometer__segment ai-thermometer__segment--positive"
              style={{
                width: `${percent(summaryQuery.data.positive, summaryQuery.data.analyzed_news)}%`,
              }}
            />
            <span
              className="ai-thermometer__segment ai-thermometer__segment--neutral"
              style={{
                width: `${percent(summaryQuery.data.neutral, summaryQuery.data.analyzed_news)}%`,
              }}
            />
            <span
              className="ai-thermometer__segment ai-thermometer__segment--negative"
              style={{
                width: `${percent(summaryQuery.data.negative, summaryQuery.data.analyzed_news)}%`,
              }}
            />
          </div>

          <ul className="ai-thermometer__list">
            {summaryQuery.data.items.map((item) => {
              const tone = translateSentiment(item.sentiment)

              return (
                <li key={item.news_reference_id}>
                  <span className={`tone-badge tone-badge--${tone.tone}`}>{tone.text}</span>
                  <span className="ai-thermometer__title">
                    {item.url ? (
                      <a href={item.url} target="_blank" rel="noopener noreferrer">
                        {item.title}
                      </a>
                    ) : (
                      item.title
                    )}
                  </span>
                  <span className="metric-hint">
                    {item.source} · {formatDate(item.published_at)}
                  </span>
                </li>
              )
            })}
          </ul>

          <p className="metric-hint">
            Muestra el tono con el que se escribieron las noticias. No indica si el precio subirá o
            bajará.
          </p>
        </>
      )}
    </section>
  )
}
