import type { NewsResponse } from '@/api/types'
import { describeRelevance, translateProviderSentiment } from '@/lib/aiInterpretation'

interface NewsCardProps {
  news: NewsResponse
}

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

export function NewsCard({ news }: NewsCardProps) {
  const relevance = describeRelevance(news.relevance)
  const providerScore = formatDecimal(news.provider_sentiment.score)
  const providerSentimentLabel = news.provider_sentiment.label
  const providerSentiment = providerSentimentLabel
    ? translateProviderSentiment(providerSentimentLabel)
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

          {relevance ? (
            <span
              className="news-card__relevance"
              title="Qué tanto trata la noticia sobre este activo, según Alpha Vantage (0 a 100)."
            >
              Relevancia {relevance}
            </span>
          ) : null}
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

        {providerSentiment ? (
          <section className="news-card__section">
            <h4>Tono general de la noticia</h4>

            <div className="news-card__sentiment">
              <span className={`news-sentiment news-sentiment--${providerSentiment.tone}`}>
                {providerSentiment.text}
              </span>

              {providerScore ? (
                <span title="Puntuación del proveedor: negativa = bajista, positiva = alcista.">
                  Puntuación {providerScore}
                </span>
              ) : null}
            </div>
          </section>
        ) : null}

        {news.ticker_sentiment.length > 0 ? (
          <section className="news-card__section">
            <h4>Tono por activo mencionado</h4>

            <div className="news-card__tickers">
              {news.ticker_sentiment.map((ticker) => {
                const sentimentScore = formatDecimal(ticker.sentiment_score)
                const tickerRelevance = describeRelevance(ticker.relevance_score)
                const tickerSentiment = translateProviderSentiment(ticker.sentiment_label)

                return (
                  <div className="news-ticker" key={`${news.reference_id}-${ticker.ticker}`}>
                    <div className="news-ticker__header">
                      <strong>{ticker.ticker}</strong>

                      <span className={`news-sentiment news-sentiment--${tickerSentiment.tone}`}>
                        {tickerSentiment.text}
                      </span>
                    </div>

                    <dl>
                      <div>
                        <dt>Puntuación</dt>
                        <dd>{sentimentScore ?? 'No disponible'}</dd>
                      </div>

                      <div>
                        <dt>Relevancia (0 a 100)</dt>
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
