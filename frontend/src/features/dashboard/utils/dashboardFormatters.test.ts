import { describe, expect, it } from 'vitest'

import {
  formatDashboardDate,
  formatDashboardLabel,
  formatDashboardMoney,
  formatDashboardPercentage,
} from './dashboardFormatters'

describe('dashboardFormatters', () => {
  it('formatea etiquetas separadas por guion bajo', () => {
    expect(formatDashboardLabel('EN_PROGRESO')).toBe('En Progreso')
  })

  it('devuelve No disponible para etiquetas vacías', () => {
    expect(formatDashboardLabel(null)).toBe('No disponible')
    expect(formatDashboardLabel(undefined)).toBe('No disponible')
    expect(formatDashboardLabel('')).toBe('No disponible')
  })

  it('conserva fechas inválidas', () => {
    expect(formatDashboardDate('fecha-invalida')).toBe('fecha-invalida')
  })

  it('devuelve No disponible cuando no existe fecha', () => {
    expect(formatDashboardDate(null)).toBe('No disponible')
  })

  it('delega el formato monetario al formatter compartido', () => {
    expect(formatDashboardMoney(null, 'MXN')).toBe('No disponible')
    expect(formatDashboardMoney('no-numerico', 'USD')).toBe('no-numerico USD')
  })

  it('formatea porcentajes con dos decimales', () => {
    expect(formatDashboardPercentage('12.345')).toBe('12.35 %')
  })

  it('maneja porcentajes ausentes o no numéricos', () => {
    expect(formatDashboardPercentage(null)).toBe('No disponible')
    expect(formatDashboardPercentage(undefined)).toBe('No disponible')
    expect(formatDashboardPercentage('pendiente')).toBe('pendiente')
  })
})
