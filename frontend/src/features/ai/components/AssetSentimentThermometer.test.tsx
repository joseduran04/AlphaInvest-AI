import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { AssetResponse } from '@/api/types'

import { AssetSentimentThermometer } from './AssetSentimentThermometer'

const useAssetSentimentSummaryMock = vi.fn()

vi.mock('@/features/ai/hooks/useAssetSentimentSummary', () => ({
  useAssetSentimentSummary: (assetId: string) => useAssetSentimentSummaryMock(assetId),
}))

const asset = { id: 'asset-1', symbol: 'NVDA', name: 'NVIDIA Corporation' } as AssetResponse

describe('AssetSentimentThermometer', () => {
  beforeEach(() => {
    useAssetSentimentSummaryMock.mockReset()
  })

  it('resume el tono de las noticias analizadas', () => {
    useAssetSentimentSummaryMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: {
        asset_id: 'asset-1',
        analyzed_news: 3,
        positive: 2,
        neutral: 0,
        negative: 1,
        items: [
          {
            news_reference_id: 'n1',
            title: 'NVIDIA supera expectativas',
            source: 'Reuters',
            url: null,
            published_at: '2026-09-23T12:00:00Z',
            sentiment: 'POSITIVO',
            confidence: '0.9',
            score: '0.8',
            analyzed_at: '2026-09-24T12:00:00Z',
          },
        ],
      },
    })

    render(<AssetSentimentThermometer asset={asset} />)

    expect(screen.getByText('2 positivas')).toHaveClass('financial-value--positive')
    expect(screen.getByText('1 negativas')).toHaveClass('financial-value--negative')
    expect(screen.getByRole('img')).toHaveAccessibleName('2 positivas, 0 neutrales, 1 negativas')
    expect(screen.getByText('Tono positivo')).toBeInTheDocument()
    expect(screen.getByText(/No indica si el precio subirá o bajará/)).toBeInTheDocument()
    expect(useAssetSentimentSummaryMock).toHaveBeenCalledWith('asset-1')
  })

  it('invita a analizar cuando no hay noticias analizadas', () => {
    useAssetSentimentSummaryMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: {
        asset_id: 'asset-1',
        analyzed_news: 0,
        positive: 0,
        neutral: 0,
        negative: 0,
        items: [],
      },
    })

    render(<AssetSentimentThermometer asset={asset} />)

    expect(screen.getByText(/Todavía no hay noticias analizadas de NVDA/)).toBeInTheDocument()
  })
})
