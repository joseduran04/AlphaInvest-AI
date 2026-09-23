import { describe, expect, it } from 'vitest'

import {
  formatRiskClassification,
  formatRiskConfidence,
  formatRiskDate,
  formatRiskScore,
} from './profileFormatters'

describe('profileFormatters', () => {
  it('formatea clasificaciones de riesgo', () => {
    expect(formatRiskClassification('MODERADO_AGRESIVO')).toBe('Moderado Agresivo')
  })

  it('formatea el puntaje con dos decimales', () => {
    expect(formatRiskScore('75.5')).toBe('75.50 / 100')
  })

  it('conserva un puntaje no numérico', () => {
    expect(formatRiskScore('pendiente')).toBe('pendiente')
  })

  it('convierte confianza decimal a porcentaje', () => {
    expect(formatRiskConfidence('0.856')).toBe('86 %')
  })

  it('maneja confianza ausente o inválida', () => {
    expect(formatRiskConfidence(null)).toBe('No disponible')
    expect(formatRiskConfidence(undefined)).toBe('No disponible')
    expect(formatRiskConfidence('pendiente')).toBe('pendiente')
  })

  it('devuelve No disponible cuando no existe fecha', () => {
    expect(formatRiskDate(null)).toBe('No disponible')
    expect(formatRiskDate(undefined)).toBe('No disponible')
  })

  it('conserva una fecha inválida', () => {
    expect(formatRiskDate('fecha-invalida')).toBe('fecha-invalida')
  })
})
