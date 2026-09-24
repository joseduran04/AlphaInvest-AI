import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { AssetAnalysisResultResponse, AssetResponse } from '@/api/types'

import { AssetAnalysisResult } from './AssetAnalysisResult'

function buildResult(): AssetAnalysisResultResponse {
  return {
    request_id: 'request-1',
    asset_id: 'asset-1',
    trend_model_version_id: 'version-1',
    price_forecast_version_id: null,
    base_date: '2026-09-22',
    target_date: '2026-09-29',
    horizon: 'CORTO_PLAZO',
    base_price: '736.60',
    predicted_price: '742.10',
    expected_return_percentage: '0.7465',
    trend: 'ALCISTA',
    confidence: '0.45',
    probabilities: { bullish: '0.45', neutral: '0.35', bearish: '0.20' },
  } as AssetAnalysisResultResponse
}

function buildAsset(symbol: string): AssetResponse {
  return { symbol, name: `${symbol} Inc.`, currency: 'USD' } as AssetResponse
}

describe('AssetAnalysisResult', () => {
  it('interpreta primero y deja las cifras técnicas en un detalle', () => {
    render(<AssetAnalysisResult result={buildResult()} asset={buildAsset('AAPL')} />)

    expect(screen.getAllByText('Sesgo alcista').length).toBeGreaterThan(0)
    expect(screen.getByText(/12 puntos por encima del 33 %/)).toBeInTheDocument()
    expect(screen.getByRole('meter', { name: 'Alcista' })).toHaveAttribute('aria-valuenow', '45')
    expect(screen.getByText('Detalle técnico').closest('details')).not.toHaveAttribute('open')
  })

  it('advierte cuando el activo no es con el que se entrenó el modelo', () => {
    render(<AssetAnalysisResult result={buildResult()} asset={buildAsset('META')} />)

    expect(screen.getByText('Modelo entrenado solo con AAPL')).toBeInTheDocument()
  })

  it('no muestra la advertencia para AAPL', () => {
    render(<AssetAnalysisResult result={buildResult()} asset={buildAsset('AAPL')} />)

    expect(screen.queryByText('Modelo entrenado solo con AAPL')).not.toBeInTheDocument()
  })

  it('explica que el precio de referencia no es una predicción específica', () => {
    render(<AssetAnalysisResult result={buildResult()} asset={buildAsset('AAPL')} />)

    expect(screen.getByText(/no es una predicción específica para esta fecha/)).toBeInTheDocument()
    expect(screen.getByText(/no una garantía de que el precio suba/)).toBeInTheDocument()
  })
})
