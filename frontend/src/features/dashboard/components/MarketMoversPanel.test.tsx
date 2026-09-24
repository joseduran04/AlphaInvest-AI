import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { MarketMoversPanel } from './MarketMoversPanel'

const useDashboardMarketMoversMock = vi.fn()

vi.mock('@/features/dashboard/hooks/useDashboardMarketMovers', () => ({
  useDashboardMarketMovers: () => useDashboardMarketMoversMock(),
}))

function mover(symbol: string, change: string, pct: string) {
  return {
    asset_id: `id-${symbol}`,
    symbol,
    name: `${symbol} Inc.`,
    currency: 'USD',
    source_name: 'Yahoo Finance',
    last_date: '2026-09-23',
    last_close: '100.00',
    previous_date: '2026-09-22',
    previous_close: '99.00',
    change,
    change_percentage: pct,
  }
}

describe('MarketMoversPanel', () => {
  beforeEach(() => {
    useDashboardMarketMoversMock.mockReset()
  })

  it('muestra ganadores en verde y perdedores en rojo', () => {
    useDashboardMarketMoversMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: {
        gainers: [mover('NVDA', '10.00', '5.0000')],
        losers: [mover('AMZN', '-5.71', '-2.2394')],
      },
    })

    render(
      <MemoryRouter>
        <MarketMoversPanel />
      </MemoryRouter>,
    )

    const gainers = screen.getByRole('heading', { name: 'Top ganadores' }).parentElement!
    const losers = screen.getByRole('heading', { name: 'Top perdedores' }).parentElement!

    expect(within(gainers).getByText('+5.00 %').parentElement).toHaveClass(
      'financial-value--positive',
    )
    expect(within(losers).getByText('-2.24 %').parentElement).toHaveClass(
      'financial-value--negative',
    )
    expect(within(gainers).getByRole('link', { name: /NVDA/ })).toHaveAttribute(
      'href',
      '/app/market/assets/id-NVDA',
    )
  })

  it('indica cuando no hubo bajas', () => {
    useDashboardMarketMoversMock.mockReturnValue({
      isPending: false,
      isError: false,
      data: { gainers: [], losers: [] },
    })

    render(
      <MemoryRouter>
        <MarketMoversPanel />
      </MemoryRouter>,
    )

    expect(screen.getByText('Ningún activo bajó en su última sesión.')).toBeInTheDocument()
  })
})
