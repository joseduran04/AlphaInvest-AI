import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { TimeSeriesChart } from './TimeSeriesChart'

describe('TimeSeriesChart', () => {
  const props = {
    title: 'Evolución',
    dates: ['2026-09-21', '2026-09-22', '2026-09-23'],
    series: [
      { key: 'a', label: 'Valor', color: 'series-1' as const, values: [100, 110, 105] },
      { key: 'b', label: 'Invertido', color: 'muted' as const, values: [100, 100, 100] },
    ],
    formatValue: (value: number) => `$${value}`,
  }

  it('dibuja una línea por serie, leyenda y tabla de datos', () => {
    const { container } = render(<TimeSeriesChart {...props} />)

    expect(container.querySelectorAll('path.chart__line')).toHaveLength(2)
    expect(screen.getAllByText('Valor').length).toBeGreaterThan(0)
    expect(screen.getByText('Ver datos en tabla')).toBeInTheDocument()
    expect(screen.getByRole('row', { name: /2026-09-22/ })).toHaveTextContent('$110')
  })

  it('muestra el tooltip con todas las series al pasar el puntero', () => {
    const { container } = render(<TimeSeriesChart {...props} />)

    fireEvent.pointerMove(container.querySelector('.chart__hit-area')!, { clientX: 5 })

    const tooltip = screen.getByRole('status')

    expect(tooltip).toHaveTextContent('$100')
    expect(tooltip).toHaveTextContent('Invertido')
  })
})
