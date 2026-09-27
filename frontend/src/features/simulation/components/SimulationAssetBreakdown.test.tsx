import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { AssetResponse, SimulationAssetResultResponse } from '@/api/types'

import { SimulationAssetBreakdown } from './SimulationAssetBreakdown'

const metaResult = {
  id: 'r-meta',
  activo_id: 'meta',
  porcentaje_asignado: '60.00',
  capital_asignado: '600.00',
  precio_inicial: '578.08',
  precio_final: '751.66',
  cantidad_inicial: '1.03791191',
  valor_final: '780.16',
  ganancia_perdida: '180.16',
  rendimiento_porcentaje: '30.03',
  volatilidad: '55.66',
  maximo_drawdown_porcentaje: '3.33',
  detalle: { aportaciones_totales: '0', cantidad_final: '1.03791191' },
} as unknown as SimulationAssetResultResponse

const metaAsset = {
  id: 'meta',
  symbol: 'META',
  name: 'Meta Platforms, Inc.',
  currency: 'USD',
  asset_type: { name: 'Acción' },
  market: { name: 'Nasdaq Stock Market' },
} as unknown as AssetResponse

describe('SimulationAssetBreakdown', () => {
  it('explica paso a paso el caso META (600 USD a 578.08)', () => {
    render(
      <SimulationAssetBreakdown
        result={metaResult}
        marketAsset={metaAsset}
        currency="USD"
        initialCapital="1000.00"
        annualizationIsRepresentative={false}
      />,
    )

    const flow = screen.getByRole('list', { name: 'Cómo se obtuvo el resultado de META' })
    expect(within(flow).getByText('Acciones compradas')).toBeInTheDocument()
    expect(within(flow).getByText('1.0379')).toBeInTheDocument()
    expect(within(flow).getByText(/\+USD\s173\.58 por acción \(\+30\.03 %\)/)).toHaveClass(
      'financial-value--positive',
    )

    expect(screen.getByText(/USD\s600\.00 ÷ USD\s578\.08/)).toBeInTheDocument()
    expect(screen.getByText(/USD\s751\.66 − USD\s578\.08/)).toBeInTheDocument()
    expect(screen.getByText(/\+USD\s173\.58 × 1\.0379 acciones/)).toBeInTheDocument()
    expect(screen.getByText(/USD\s600\.00 \+ USD\s180\.16/)).toBeInTheDocument()
  })

  it('pliega la volatilidad anualizada en periodos cortos', () => {
    render(
      <SimulationAssetBreakdown
        result={metaResult}
        marketAsset={metaAsset}
        currency="USD"
        initialCapital="1000.00"
        annualizationIsRepresentative={false}
      />,
    )

    const details = screen.getByText('Datos técnicos').closest('details')
    expect(within(details as HTMLElement).getByText('Volatilidad anualizada')).toBeInTheDocument()
  })
})

describe('SimulationAssetBreakdown con aportaciones', () => {
  it('separa la ganancia registrada de la que descuenta aportaciones', () => {
    const withContributions = {
      ...metaResult,
      valor_final: '900.00',
      ganancia_perdida: '300.00',
      detalle: { aportaciones_totales: '100.00', cantidad_final: '1.19734' },
    } as unknown as SimulationAssetResultResponse

    render(
      <SimulationAssetBreakdown
        result={withContributions}
        marketAsset={metaAsset}
        currency="USD"
        initialCapital="1000.00"
        annualizationIsRepresentative
      />,
    )

    expect(screen.getByText(/USD\s900\.00 − USD\s600\.00 asignados/)).toBeInTheDocument()
    expect(screen.getByText(/= \+USD\s200\.00/)).toBeInTheDocument()
  })
})
