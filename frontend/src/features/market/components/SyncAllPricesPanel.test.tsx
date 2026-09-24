import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactNode } from 'react'
import { describe, expect, it, vi } from 'vitest'

import { synchronizeAssetPricesRequest } from '@/features/market/api/marketApi'

import { SyncAllPricesPanel } from './SyncAllPricesPanel'

vi.mock('@/features/market/hooks/useAssets', () => ({
  useAssets: () => ({
    data: {
      items: [
        { id: 'a1', symbol: 'AAPL' },
        { id: 'a2', symbol: 'WALMEX' },
        { id: 'a3', symbol: 'META' },
      ],
    },
  }),
}))

vi.mock('@/features/market/api/marketApi', () => ({
  synchronizeAssetPricesRequest: vi.fn(),
}))

function wrapper({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>
}

describe('SyncAllPricesPanel', () => {
  it('sincroniza cada activo y reporta los que fallaron', async () => {
    const mocked = vi.mocked(synchronizeAssetPricesRequest)
    mocked.mockImplementation(async (assetId: string) => {
      if (assetId === 'a2') {
        throw new Error('Yahoo Finance no devolvió precios')
      }

      return {} as Awaited<ReturnType<typeof synchronizeAssetPricesRequest>>
    })

    render(<SyncAllPricesPanel />, { wrapper })

    await userEvent.click(screen.getByRole('button', { name: 'Sincronizar todos los precios' }))

    expect(await screen.findByText('2 de 3 activos actualizados.')).toBeInTheDocument()
    expect(screen.getByText('WALMEX: Yahoo Finance no devolvió precios')).toBeInTheDocument()
    expect(mocked).toHaveBeenCalledTimes(3)
    expect(mocked.mock.calls.map(([id]) => id)).toEqual(['a1', 'a2', 'a3'])
  })
})
