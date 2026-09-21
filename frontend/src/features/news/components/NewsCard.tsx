import type { NewsResponse } from '@/api/types'

interface NewsCardProps {
  news: NewsResponse
}

type SentimentTone = 'positive' | 'negative' | 'neutral'

function formatPublishedAt(value: string): string {
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatDecimal(value: string | null): string | null {
  if (value === null) {
    return null
  }

  const parsed = Number(value)

  if (!Number.isFinite(parsed)) {
    return null
  }

  return parsed.toFixed(2)
}

function getSentimentTone(label: string): SentimentTone {
  const normalizedLabel = label.trim().toLowerCase()

  if (normalizedLabel.includes('bullish') || normalizedLabel.includes('positive')) {
    return 'positive'
  }

  if (normalizedLabel.includes('bearish') || normalizedLabel.includes('negative')) {
    return 'negative'
  }

  return 'neutral'
}

export function NewsCard({ news }: NewsCardProps) {
  const relevance = formatDecimal(news.relevance)
  const providerScore = formatDecimal(news.provider_sentiment.score)
  const providerSentimentLabel = news.provider_sentiment.label
  const providerSentimentTone = providerSentimentLabel
    ? getSentimentTone(providerSentimentLabel)
    : null

  return (
    <article className="news-card">
      {news.banner_image ? (
        <div className="news-card__image">
          <img src={news.banner_image} alt="" loading="lazy" />
        </div>
      ) : null}

      <div className="news-card__content">
        <header className="news-card__header">
          <div className="news-card__source">
            <strong>{news.source}</strong>
            <span>{formatPublishedAt(news.published_at)}</span>
          </div>

          {relevance ? <span className="news-card__relevance">Relevancia {relevance}</span> : null}
        </header>

        <div className="news-card__body">
          <h3>{news.title}</h3>
          <p>{news.summary}</p>
        </div>

        {news.topics.length > 0 ? (
          <section className="news-card__section">
            <h4>Temas</h4>

            <div className="news-card__topics">
              {news.topics.slice(0, 4).map((topic) => {
                const topicRelevance = formatDecimal(topic.relevance_score)

                return (
                  <span key={`${news.reference_id}-${topic.topic}`}>
                    {topic.topic}
                    {topicRelevance ? ` · ${topicRelevance}` : ''}
                  </span>
                )
              })}
            </div>
          </section>
        ) : null}

        {providerSentimentLabel && providerSentimentTone ? (
          <section className="news-card__section">
            <h4>Sentimiento general</h4>

            <div className="news-card__sentiment">
              <span className={`news-sentiment news-sentiment--${providerSentimentTone}`}>
                {providerSentimentLabel}
              </span>

              {providerScore ? <span>Score {providerScore}</span> : null}
            </div>
          </section>
        ) : null}

        {news.ticker_sentiment.length > 0 ? (
          <section className="news-card__section">
            <h4>Sentimiento por activo</h4>

            <div className="news-card__tickers">
              {news.ticker_sentiment.map((ticker) => {
                const sentimentScore = formatDecimal(ticker.sentiment_score)
                const tickerRelevance = formatDecimal(ticker.relevance_score)
                const sentimentTone = getSentimentTone(ticker.sentiment_label)

                return (
                  <div className="news-ticker" key={`${news.reference_id}-${ticker.ticker}`}>
                    <div className="news-ticker__header">
                      <strong>{ticker.ticker}</strong>

                      <span className={`news-sentiment news-sentiment--${sentimentTone}`}>
                        {ticker.sentiment_label}
                      </span>
                    </div>

                    <dl>
                      <div>
                        <dt>Sentimiento</dt>
                        <dd>{sentimentScore ?? 'No disponible'}</dd>
                      </div>

                      <div>
                        <dt>Relevancia</dt>
                        <dd>{tickerRelevance ?? 'No disponible'}</dd>
                      </div>
                    </dl>
                  </div>
                )
              })}
            </div>
          </section>
        ) : null}

        <dl className="news-card__metadata">
          {news.authors.length > 0 ? (
            <div>
              <dt>Autores</dt>
              <dd>{news.authors.join(', ')}</dd>
            </div>
          ) : null}

          {news.category_within_source ? (
            <div>
              <dt>Categoría</dt>
              <dd>{news.category_within_source}</dd>
            </div>
          ) : null}
        </dl>

        <footer className="news-card__footer">
          <div>
            {news.source_domain ? <span>{news.source_domain}</span> : null}
            {news.language ? <span>Idioma: {news.language.toUpperCase()}</span> : null}
          </div>

          {news.url ? (
            <a
              className="button button--secondary"
              href={news.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Leer fuente
            </a>
          ) : null}
        </footer>
      </div>
    </article>
  )
}
