import type { PropsWithChildren } from 'react'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { PortfolioCreateRequest } from '@/api/types'
import { createPortfolioRequest } from '@/features/portfolio/api/portfolioApi'

import { portfolioQueryKeys } from './portfolioQueryKeys'
import { useCreatePortfolio } from './useCreatePortfolio'

vi.mock('@/features/portfolio/api/portfolioApi', () => ({
  createPortfolioRequest: vi.fn(),
}))

const mockedCreatePortfolioRequest = vi.mocked(createPortfolioRequest)

function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

function createWrapper(queryClient: QueryClient) {
  return function Wrapper({ children }: PropsWithChildren) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  }
}

describe('useCreatePortfolio', () => {
  beforeEach(() => {
    mockedCreatePortfolioRequest.mockReset()
  })

  it('crea un portafolio utilizando los datos recibidos', async () => {
    const queryClient = createTestQueryClient()

    const data: PortfolioCreateRequest = {
      nombre: 'Portafolio de prueba',
      descripcion: 'Portafolio utilizado en pruebas unitarias',
      moneda_base: 'USD',
      capital_inicial: 10000,
      tipo: 'VIRTUAL',
      fecha_inicio: null,
    }

    mockedCreatePortfolioRequest.mockResolvedValue(
      {} as Awaited<ReturnType<typeof createPortfolioRequest>>,
    )

    const { result } = renderHook(() => useCreatePortfolio(), {
      wrapper: createWrapper(queryClient),
    })

    await act(async () => {
      await result.current.mutateAsync(data)
    })

    expect(mockedCreatePortfolioRequest).toHaveBeenCalledTimes(1)
    expect(mockedCreatePortfolioRequest).toHaveBeenCalledWith(data)
  })

  it('invalida la lista de portafolios después de una creación exitosa', async () => {
    const queryClient = createTestQueryClient()
    const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries')

    const data: PortfolioCreateRequest = {
      nombre: 'Portafolio de prueba',
      descripcion: null,
      moneda_base: 'USD',
      capital_inicial: '5000',
      tipo: 'VIRTUAL',
      fecha_inicio: null,
    }

    mockedCreatePortfolioRequest.mockResolvedValue(
      {} as Awaited<ReturnType<typeof createPortfolioRequest>>,
    )

    const { result } = renderHook(() => useCreatePortfolio(), {
      wrapper: createWrapper(queryClient),
    })

    await act(async () => {
      await result.current.mutateAsync(data)
    })

    expect(invalidateQueriesSpy).toHaveBeenCalledWith({
      queryKey: portfolioQueryKeys.listsRoot(),
    })
  })

  it('no invalida la lista cuando la creación falla', async () => {
    const queryClient = createTestQueryClient()
    const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries')

    const data: PortfolioCreateRequest = {
      nombre: 'Portafolio con error',
      moneda_base: 'USD',
      capital_inicial: 1000,
      tipo: 'VIRTUAL',
    }

    const error = new Error('No fue posible crear el portafolio')

    mockedCreatePortfolioRequest.mockRejectedValue(error)

    const { result } = renderHook(() => useCreatePortfolio(), {
      wrapper: createWrapper(queryClient),
    })

    await expect(
      act(async () => {
        await result.current.mutateAsync(data)
      }),
    ).rejects.toThrow('No fue posible crear el portafolio')

    expect(invalidateQueriesSpy).not.toHaveBeenCalled()
  })
})
