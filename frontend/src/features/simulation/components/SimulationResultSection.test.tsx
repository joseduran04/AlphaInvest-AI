import { render, screen, within } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { SimulationResultResponse } from '@/api/types'

import { SimulationResultSection } from './SimulationResultSection'

const useSimulationResultMock = vi.fn()

vi.mock('@/features/simulation/hooks/useSimulationResult', () => ({
  useSimulationResult: (executionId: string) => useSimulationResultMock(executionId),
}))

vi.mock('@/features/market/hooks/useDailyCloses', () => ({
  useDailyCloses: () => ({
    closesByAsset: new Map(),
    isPending: false,
    isError: false,
    errorMessage: null,
  }),
}))

vi.mock('@/features/market/hooks/useAssets', () => ({
  useAssets: () => ({ data: { items: [] }, isError: false }),
}))

function buildResult(overrides: Partial<SimulationResultResponse> = {}): SimulationResultResponse {
  return {
    id: 'result-1',
    ejecucion_id: 'execution-1',
    capital_inicial: '10000.00',
    aportaciones_totales: '0.00',
    capital_final: '11201.13',
    ganancia_perdida: '1201.13',
    rendimiento_total_porcentaje: '12.0113',
    rendimiento_anualizado_porcentaje: '6181.35',
    volatilidad_anualizada: '42.20',
    indice_sharpe: '146.494',
    maximo_drawdown_porcentaje: '3.10',
    valor_en_riesgo: null,
    nivel_confianza_var: null,
    mejor_escenario: null,
    peor_escenario: null,
    mediana_escenarios: null,
    probabilidad_ganancia: null,
    moneda: 'USD',
    resumen: {
      fecha_inicio_efectiva: '2026-09-01',
      fecha_fin_efectiva: '2026-09-11',
      comisiones_totales: '0',
    },
    fecha_registro: '2026-09-23T00:00:00Z',
    activos: [],
    ...overrides,
  } as SimulationResultResponse
}

describe('SimulationResultSection', () => {
  beforeEach(() => {
    useSimulationResultMock.mockReset()
  })

  it('avisa cuando el periodo efectivo es más corto que el solicitado (caso META)', () => {
    useSimulationResultMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: buildResult(),
    })

    render(
      <SimulationResultSection
        executionId="execution-1"
        onClose={() => undefined}
        requestedStartDate="2026-09-01"
        requestedEndDate="2026-09-23"
      />,
    )

    expect(
      screen.getByText('El periodo simulado es más corto que el solicitado'),
    ).toBeInTheDocument()
    expect(screen.getByText('Periodo solicitado')).toBeInTheDocument()
  })

  it('no avisa cuando la diferencia es solo un fin de semana', () => {
    useSimulationResultMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: buildResult(),
    })

    render(
      <SimulationResultSection
        executionId="execution-1"
        onClose={() => undefined}
        requestedStartDate="2026-09-01"
        requestedEndDate="2026-09-13"
      />,
    )

    expect(
      screen.queryByText('El periodo simulado es más corto que el solicitado'),
    ).not.toBeInTheDocument()
  })

  it('prioriza el rendimiento del periodo y relega la anualización en periodos cortos', () => {
    useSimulationResultMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: buildResult(),
    })

    render(<SimulationResultSection executionId="execution-1" onClose={() => undefined} />)

    const periodReturn = screen.getByText('Rendimiento del periodo').closest('div')
    expect(periodReturn).not.toBeNull()
    expect(within(periodReturn as HTMLElement).getByText('12.01 %')).toHaveClass(
      'financial-value--positive',
    )
    expect(
      screen.getByText('Lo que habría ganado o perdido el capital en 10 días naturales.'),
    ).toBeInTheDocument()

    const details = screen
      .getByText('Métricas anualizadas (poco representativas en periodos cortos)')
      .closest('details')
    expect(details).not.toBeNull()
    expect(details).not.toHaveAttribute('open')
    expect(within(details as HTMLElement).getByText('6181.35 %')).toBeInTheDocument()
  })

  it('muestra la anualización directamente en periodos de un año o más', () => {
    useSimulationResultMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: buildResult({
        rendimiento_anualizado_porcentaje: '8.50',
        resumen: {
          fecha_inicio_efectiva: '2024-01-02',
          fecha_fin_efectiva: '2026-09-11',
          comisiones_totales: '0',
        },
      }),
    })

    render(<SimulationResultSection executionId="execution-1" onClose={() => undefined} />)

    expect(
      screen.queryByText('Métricas anualizadas (poco representativas en periodos cortos)'),
    ).not.toBeInTheDocument()
    expect(screen.getAllByText('8.50 %').length).toBeGreaterThan(0)
  })

  it('colorea pérdidas en rojo', () => {
    useSimulationResultMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: buildResult({ ganancia_perdida: '-250.00', rendimiento_total_porcentaje: '-2.5' }),
    })

    render(<SimulationResultSection executionId="execution-1" onClose={() => undefined} />)

    expect(screen.getByText('-2.50 %')).toHaveClass('financial-value--negative')
  })
})
