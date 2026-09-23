import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { PageEmptyState } from './PageEmptyState'
import { PageErrorState } from './PageErrorState'
import { PageLoadingState } from './PageLoadingState'
import { PageState } from './PageState'

describe('PageState', () => {
  it('renderiza título, descripción y acción', () => {
    render(
      <PageState
        title="Estado de prueba"
        description="Descripción de prueba"
        action={<button type="button">Continuar</button>}
      />,
    )

    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Estado de prueba' })).toBeInTheDocument()
    expect(screen.getByText('Descripción de prueba')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Continuar' })).toBeInTheDocument()
  })

  it('permite omitir descripción y acción', () => {
    render(<PageState title="Solo título" />)

    expect(screen.getByRole('heading', { name: 'Solo título' })).toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})

describe('PageLoadingState', () => {
  it('muestra el mensaje predeterminado', () => {
    render(<PageLoadingState />)

    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Cargando información...' })).toBeInTheDocument()
    expect(screen.getByText('Espera un momento.')).toBeInTheDocument()
  })

  it('permite personalizar el mensaje', () => {
    render(<PageLoadingState message="Cargando portafolios..." />)

    expect(screen.getByRole('heading', { name: 'Cargando portafolios...' })).toBeInTheDocument()
  })
})

describe('PageEmptyState', () => {
  it('muestra el título predeterminado', () => {
    render(<PageEmptyState />)

    expect(
      screen.getByRole('heading', { name: 'No hay información disponible' }),
    ).toBeInTheDocument()
  })

  it('renderiza contenido y acción personalizados', () => {
    render(
      <PageEmptyState
        title="Sin portafolios"
        description="Crea tu primer portafolio."
        action={<button type="button">Crear portafolio</button>}
      />,
    )

    expect(screen.getByRole('heading', { name: 'Sin portafolios' })).toBeInTheDocument()
    expect(screen.getByText('Crea tu primer portafolio.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Crear portafolio' })).toBeInTheDocument()
  })
})

describe('PageErrorState', () => {
  it('muestra el estado de error predeterminado', () => {
    render(<PageErrorState />)

    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'No fue posible cargar la información',
      }),
    ).toBeInTheDocument()
    expect(screen.getByText('Ocurrió un problema al procesar la solicitud.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Reintentar' })).not.toBeInTheDocument()
  })

  it('ejecuta onRetry al seleccionar Reintentar', () => {
    const onRetry = vi.fn()

    render(
      <PageErrorState
        title="Error de mercado"
        message="No fue posible consultar los activos."
        onRetry={onRetry}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Reintentar' }))

    expect(onRetry).toHaveBeenCalledTimes(1)
  })
})
