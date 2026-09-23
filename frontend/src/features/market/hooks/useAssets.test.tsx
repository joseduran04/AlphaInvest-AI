import type { PropsWithChildren } from 'react'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { assetsRequest } from '@/features/market/api/marketApi'

import { marketQueryKeys } from './marketQueryKeys'
import { useAssets } from './useAssets'

vi.mock('@/features/market/api/marketApi', () => ({
  assetsRequest: vi.fn(),
}))

const mockedAssetsRequest = vi.mocked(assetsRequest)

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return function Wrapper({ children }: PropsWithChildren) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  }
}

describe('useAssets', () => {
  beforeEach(() => {
    mockedAssetsRequest.mockReset()
  })

  it('consulta activos utilizando los parámetros recibidos', async () => {
    const params = {
      limit: 10,
      offset: 0,
    }

    mockedAssetsRequest.mockResolvedValue({} as Awaited<ReturnType<typeof assetsRequest>>)

    const { result } = renderHook(() => useAssets(params), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockedAssetsRequest).toHaveBeenCalledTimes(1)
    expect(mockedAssetsRequest).toHaveBeenCalledWith(params)
  })

  it('no ejecuta la consulta cuando enabled es false', async () => {
    const params = {
      limit: 10,
      offset: 0,
    }

    const { result } = renderHook(() => useAssets(params, false), {
      wrapper: createWrapper(),
    })

    expect(result.current.fetchStatus).toBe('idle')

    await waitFor(() => {
      expect(mockedAssetsRequest).not.toHaveBeenCalled()
    })
  })

  it('utiliza la query key definida para la lista de activos', () => {
    const params = {
      limit: 10,
      offset: 0,
    }

    expect(marketQueryKeys.assets(params)).toEqual(['market', 'assets', 'list', params])
  })
})
