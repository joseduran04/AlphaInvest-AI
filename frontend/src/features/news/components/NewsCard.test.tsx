import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { NewsResponse } from '@/api/types'

import { NewsCard } from './NewsCard'

function buildNews(): NewsResponse {
  return {
    reference_id: 'news-1',
    asset_id: 'asset-1',
    mongo_document_id: 'mongo-1',
    title: 'Apple presenta resultados',
    source: 'Reuters',
    url: null,
    published_at: '2026-09-23T12:00:00Z',
    language: 'en',
    relevance: '0.786',
    authors: [],
    summary: 'Resumen de la noticia.',
    banner_image: null,
    category_within_source: null,
    source_domain: null,
    topics: [],
    provider_sentiment: { score: '0.21', label: 'Somewhat-Bullish' },
    ticker_sentiment: [
      {
        ticker: 'AAPL',
        relevance_score: '0.9',
        sentiment_score: '-0.4',
        sentiment_label: 'Bearish',
      },
    ],
  } as NewsResponse
}

describe('NewsCard', () => {
  it('traduce las etiquetas del proveedor y la relevancia', () => {
    render(<NewsCard news={buildNews()} />)

    expect(screen.getByText('Relevancia 79 de 100')).toBeInTheDocument()
    expect(screen.getByText('Sesgo alcista moderado')).toHaveClass('news-sentiment--positive')
    expect(screen.getByText('Sesgo bajista')).toHaveClass('news-sentiment--negative')
    expect(screen.getByText('90 de 100')).toBeInTheDocument()
  })
})
