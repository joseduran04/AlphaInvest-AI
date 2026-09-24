import { describe, expect, it } from 'vitest'

import {
  getCalendarDaysBetween,
  getPeriodShortfall,
  isAnnualizationRepresentative,
} from './periodMetrics'

describe('getCalendarDaysBetween', () => {
  it('calcula días naturales entre fechas ISO', () => {
    expect(getCalendarDaysBetween('2026-09-01', '2026-09-11')).toBe(10)
    expect(getCalendarDaysBetween('2026-09-01T00:00:00', '2026-09-23')).toBe(22)
  })

  it('devuelve null con fechas ausentes o inválidas', () => {
    expect(getCalendarDaysBetween(null, '2026-09-11')).toBeNull()
    expect(getCalendarDaysBetween('no-es-fecha', '2026-09-11')).toBeNull()
  })
})

describe('isAnnualizationRepresentative', () => {
  it('no considera representativos periodos menores a un año', () => {
    expect(isAnnualizationRepresentative('2026-09-01', '2026-09-11')).toBe(false)
    expect(isAnnualizationRepresentative('2025-09-12', '2026-09-11')).toBe(false)
  })

  it('considera representativos periodos de un año o más', () => {
    expect(isAnnualizationRepresentative('2025-09-11', '2026-09-11')).toBe(true)
    expect(isAnnualizationRepresentative('2020-01-01', '2026-09-11')).toBe(true)
  })

  it('no es representativo si faltan fechas', () => {
    expect(isAnnualizationRepresentative(null, null)).toBe(false)
  })
})

describe('getPeriodShortfall', () => {
  it('detecta el recorte del caso META (fin solicitado 23/09, efectivo 11/09)', () => {
    expect(
      getPeriodShortfall({
        requestedStart: '2026-09-01',
        requestedEnd: '2026-09-23',
        effectiveStart: '2026-09-01',
        effectiveEnd: '2026-09-11',
      }),
    ).toEqual({ startDays: 0, endDays: 12 })
  })

  it('devuelve cero cuando no hay datos', () => {
    expect(
      getPeriodShortfall({
        requestedStart: null,
        requestedEnd: null,
        effectiveStart: '2026-09-01',
        effectiveEnd: '2026-09-11',
      }),
    ).toEqual({ startDays: 0, endDays: 0 })
  })
})
