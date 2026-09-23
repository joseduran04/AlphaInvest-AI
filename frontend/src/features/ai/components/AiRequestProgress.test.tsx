import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { AiRequestProgress } from './AiRequestProgress'

describe('AiRequestProgress', () => {
  it('muestra el estado de espera predeterminado para una solicitud pendiente sin progreso', () => {
    render(
      <AiRequestProgress
        status="PENDIENTE"
        progressPercentage="0"
        executingTitle="Procesando análisis"
        executingDescription="El análisis está en ejecución."
      />,
    )

    expect(screen.getByText('Esperando procesamiento')).toBeInTheDocument()
    expect(
      screen.getByText('La solicitud fue registrada y está esperando ser procesada.'),
    ).toBeInTheDocument()
    expect(screen.getByText('En espera')).toBeInTheDocument()
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
  })

  it('permite personalizar el estado de espera', () => {
    render(
      <AiRequestProgress
        status="PENDIENTE"
        progressPercentage="0"
        pendingTitle="Análisis pendiente"
        pendingDescription="Esperando disponibilidad del worker."
        executingTitle="Procesando análisis"
        executingDescription="El análisis está en ejecución."
      />,
    )

    expect(screen.getByText('Análisis pendiente')).toBeInTheDocument()
    expect(screen.getByText('Esperando disponibilidad del worker.')).toBeInTheDocument()
  })

  it('muestra el estado de ejecución y el porcentaje de progreso', () => {
    render(
      <AiRequestProgress
        status="EJECUTANDO"
        progressPercentage="42.5"
        executingTitle="Procesando análisis"
        executingDescription="El análisis está en ejecución."
      />,
    )

    expect(screen.getByText('Procesando análisis')).toBeInTheDocument()
    expect(screen.getByText('El análisis está en ejecución.')).toBeInTheDocument()

    const progress = screen.getByRole('progressbar')

    expect(progress).toHaveAttribute('max', '100')
    expect(progress).toHaveAttribute('value', '42.5')
    expect(screen.getByText('42.5 %')).toBeInTheDocument()
    expect(screen.queryByText('En espera')).not.toBeInTheDocument()
  })

  it('limita el progreso superior a 100', () => {
    render(
      <AiRequestProgress
        status="EJECUTANDO"
        progressPercentage="150"
        executingTitle="Procesando análisis"
        executingDescription="El análisis está en ejecución."
      />,
    )

    expect(screen.getByRole('progressbar')).toHaveAttribute('value', '100')
    expect(screen.getByText('100 %')).toBeInTheDocument()
  })

  it('limita el progreso negativo a 0', () => {
    render(
      <AiRequestProgress
        status="EJECUTANDO"
        progressPercentage="-25"
        executingTitle="Procesando análisis"
        executingDescription="El análisis está en ejecución."
      />,
    )

    expect(screen.getByRole('progressbar')).toHaveAttribute('value', '0')
    expect(screen.getByText('0 %')).toBeInTheDocument()
  })

  it('normaliza un progreso no numérico a 0', () => {
    render(
      <AiRequestProgress
        status="EJECUTANDO"
        progressPercentage="no-disponible"
        executingTitle="Procesando análisis"
        executingDescription="El análisis está en ejecución."
      />,
    )

    expect(screen.getByRole('progressbar')).toHaveAttribute('value', '0')
    expect(screen.getByText('0 %')).toBeInTheDocument()
  })

  it('una solicitud pendiente con progreso utiliza el estado de ejecución', () => {
    render(
      <AiRequestProgress
        status="PENDIENTE"
        progressPercentage="10"
        executingTitle="Procesamiento iniciado"
        executingDescription="La solicitud ya reporta progreso."
      />,
    )

    expect(screen.getByText('Procesamiento iniciado')).toBeInTheDocument()
    expect(screen.getByText('La solicitud ya reporta progreso.')).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toHaveAttribute('value', '10')
    expect(screen.getByText('10 %')).toBeInTheDocument()
    expect(screen.queryByText('En espera')).not.toBeInTheDocument()
  })
})
