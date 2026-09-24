import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { AssetResponse, SimulationResultResponse } from '@/api/types'

import { SimulationCharts } from './SimulationCharts'

vi.mock('@/features/market/hooks/useDailyCloses', () => ({
  useDailyCloses: () => ({
    closesByAsset: new Map([
      [
        'spy',
        new Map([
          ['2026-09-01', 500],
          ['2026-09-11', 510],
        ]),
      ],
    ]),
    isPending: false,
    isError: false,
    errorMessage: null,
  }),
}))

function buildResult(resumen: Record<string, unknown>): SimulationResultResponse {
  return {
    moneda: 'USD',
    resumen,
    activos: [
      {
        id: 'r1',
        activo_id: 'meta',
        ganancia_perdida: '1201.13',
        rendimiento_porcentaje: '12.01',
      },
    ],
  } as unknown as SimulationResultResponse
}

const spy = { id: 'spy', symbol: 'SPY' } as AssetResponse
const assets = new Map([['meta', { id: 'meta', symbol: 'META' } as AssetResponse]])

describe('SimulationCharts', () => {
  it('grafica la evolución, la comparación con el S&P 500 y el resultado por activo', () => {
    render(
      <SimulationCharts
        result={buildResult({
          evolucion: [
            { fecha: '2026-09-01', valor: '10000', aportado: '10000' },
            { fecha: '2026-09-11', valor: '11201.13', aportado: '10000' },
          ],
        })}
        marketAssetsById={assets}
        benchmarkAsset={spy}
      />,
    )

    expect(screen.getByText('Valor del portafolio contra capital aportado')).toBeInTheDocument()
    expect(screen.getByText('Rendimiento contra el S&P 500')).toBeInTheDocument()
    expect(screen.getByText('Resultado por activo')).toBeInTheDocument()
    expect(screen.getAllByText('S&P 500 (SPY)').length).toBeGreaterThan(0)
  })

  it('pide volver a ejecutar cuando no hay evolución guardada', () => {
    render(
      <SimulationCharts result={buildResult({})} marketAssetsById={assets} benchmarkAsset={spy} />,
    )

    expect(screen.getByText(/no guardó su evolución diaria/)).toBeInTheDocument()
  })
})
