import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { rangeStartDate } from '@/lib/priceRanges'

import { AssetPriceChart } from './AssetPriceChart'

const usePriceSeriesMock = vi.fn()

vi.mock('@/features/market/hooks/usePriceSeries', () => ({
  usePriceSeries: (assetId: string, startDate: string | null) =>
    usePriceSeriesMock(assetId, startDate),
}))

function series(change: string, pct: string) {
  return {
    isPending: false,
    isError: false,
    isFetching: false,
    data: {
      asset_id: 'meta',
      currency: 'USD',
      points: [
        { date: '2026-09-22', close: '736.60' },
        { date: '2026-09-24', close: '770.815' },
      ],
      first_close: '736.60',
      last_close: '770.815',
      change,
      change_percentage: pct,
      sampled: false,
    },
  }
}

describe('rangeStartDate', () => {
  it('calcula el inicio del rango y null para el máximo', () => {
    const today = new Date(2026, 8, 24)

    expect(rangeStartDate(1, today)).toBe('2026-08-24')
    expect(rangeStartDate(12, today)).toBe('2025-09-24')
    expect(rangeStartDate(null, today)).toBeNull()
  })
})

describe('AssetPriceChart', () => {
  beforeEach(() => {
    usePriceSeriesMock.mockReset()
  })

  it('dibuja la línea en verde cuando el periodo sube y permite cambiar el rango', async () => {
    usePriceSeriesMock.mockReturnValue(series('34.215', '4.6460'))

    const { container } = render(<AssetPriceChart assetId="meta" symbol="META" />)

    expect(container.querySelector('path.chart__stroke--positive')).not.toBeNull()
    expect(screen.getByText(/\+4\.65 %/)).toHaveClass('financial-value--positive')

    await userEvent.click(screen.getByRole('button', { name: 'Máx' }))

    expect(usePriceSeriesMock).toHaveBeenLastCalledWith('meta', null)
    expect(screen.getByRole('button', { name: 'Máx' })).toHaveAttribute('aria-pressed', 'true')
  })

  it('usa rojo cuando el periodo baja', () => {
    usePriceSeriesMock.mockReturnValue(series('-5.00', '-0.6700'))

    const { container } = render(<AssetPriceChart assetId="meta" symbol="META" />)

    expect(container.querySelector('path.chart__stroke--negative')).not.toBeNull()
  })
})
