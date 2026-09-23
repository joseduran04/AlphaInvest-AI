import type { PropsWithChildren } from 'react'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/api/errors'
import { createPortfolioRequest } from '@/features/portfolio/api/portfolioApi'

import { CreatePortfolioForm } from './CreatePortfolioForm'

vi.mock('@/features/portfolio/api/portfolioApi', () => ({
  createPortfolioRequest: vi.fn(),
}))

const mockedCreatePortfolioRequest = vi.mocked(createPortfolioRequest)

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return function Wrapper({ children }: PropsWithChildren) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  }
}

describe('CreatePortfolioForm', () => {
  beforeEach(() => {
    mockedCreatePortfolioRequest.mockReset()
  })

  it('envía los datos normalizados y notifica la creación exitosa', async () => {
    const user = userEvent.setup()
    const onCancel = vi.fn()
    const onCreated = vi.fn()

    mockedCreatePortfolioRequest.mockResolvedValue(
      {} as Awaited<ReturnType<typeof createPortfolioRequest>>,
    )

    render(<CreatePortfolioForm onCancel={onCancel} onCreated={onCreated} />, {
      wrapper: createWrapper(),
    })

    await user.type(screen.getByLabelText('Nombre'), '  Portafolio tecnológico  ')
    await user.type(screen.getByLabelText('Descripción'), '  Estrategia de crecimiento  ')
    await user.clear(screen.getByLabelText('Moneda base'))
    await user.type(screen.getByLabelText('Moneda base'), 'mxn')
    await user.type(screen.getByLabelText('Capital inicial'), '15000.50')
    await user.selectOptions(screen.getByLabelText('Tipo'), 'SIMULADO')
    await user.type(screen.getByLabelText('Fecha de inicio'), '2026-09-22')

    await user.click(screen.getByRole('button', { name: 'Crear portafolio' }))

    await waitFor(() => {
      expect(mockedCreatePortfolioRequest).toHaveBeenCalledWith({
        nombre: 'Portafolio tecnológico',
        descripcion: 'Estrategia de crecimiento',
        moneda_base: 'MXN',
        capital_inicial: '15000.5',
        tipo: 'SIMULADO',
        fecha_inicio: '2026-09-22',
      })
    })

    expect(mockedCreatePortfolioRequest).toHaveBeenCalledTimes(1)
    expect(onCreated).toHaveBeenCalledTimes(1)
    expect(onCancel).not.toHaveBeenCalled()
  })

  it('impide enviar datos inválidos y muestra los errores de validación', async () => {
    const user = userEvent.setup()

    render(<CreatePortfolioForm onCancel={vi.fn()} onCreated={vi.fn()} />, {
      wrapper: createWrapper(),
    })

    await user.click(screen.getByRole('button', { name: 'Crear portafolio' }))

    expect(await screen.findByText('Ingresa un nombre para el portafolio.')).toBeInTheDocument()
    expect(screen.getByText('Ingresa el capital inicial.')).toBeInTheDocument()

    expect(mockedCreatePortfolioRequest).not.toHaveBeenCalled()
  })

  it('convierte los campos opcionales vacíos a null', async () => {
    const user = userEvent.setup()

    mockedCreatePortfolioRequest.mockResolvedValue(
      {} as Awaited<ReturnType<typeof createPortfolioRequest>>,
    )

    render(<CreatePortfolioForm onCancel={vi.fn()} onCreated={vi.fn()} />, {
      wrapper: createWrapper(),
    })

    await user.type(screen.getByLabelText('Nombre'), 'Portafolio básico')
    await user.type(screen.getByLabelText('Capital inicial'), '1000')

    await user.click(screen.getByRole('button', { name: 'Crear portafolio' }))

    await waitFor(() => {
      expect(mockedCreatePortfolioRequest).toHaveBeenCalledWith({
        nombre: 'Portafolio básico',
        descripcion: null,
        moneda_base: 'USD',
        capital_inicial: '1000',
        tipo: 'VIRTUAL',
        fecha_inicio: null,
      })
    })
  })

  it('muestra el mensaje correspondiente cuando la API responde con conflicto 409', async () => {
    const user = userEvent.setup()

    mockedCreatePortfolioRequest.mockRejectedValue(
      new ApiError({
        kind: 'http',
        status: 409,
        message: 'Conflicto al crear el portafolio',
      }),
    )

    render(<CreatePortfolioForm onCancel={vi.fn()} onCreated={vi.fn()} />, {
      wrapper: createWrapper(),
    })

    await user.type(screen.getByLabelText('Nombre'), 'Portafolio duplicado')
    await user.type(screen.getByLabelText('Capital inicial'), '5000')

    await user.click(screen.getByRole('button', { name: 'Crear portafolio' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'No fue posible crear el portafolio.',
    )
    expect(screen.getByRole('alert')).toHaveTextContent(
      'No fue posible crear el portafolio porque existe un conflicto con los datos registrados.',
    )
  })

  it('ejecuta onCancel al cancelar la creación', async () => {
    const user = userEvent.setup()
    const onCancel = vi.fn()

    render(<CreatePortfolioForm onCancel={onCancel} onCreated={vi.fn()} />, {
      wrapper: createWrapper(),
    })

    await user.click(screen.getByRole('button', { name: 'Cancelar' }))

    expect(onCancel).toHaveBeenCalledTimes(1)
    expect(mockedCreatePortfolioRequest).not.toHaveBeenCalled()
  })
})
