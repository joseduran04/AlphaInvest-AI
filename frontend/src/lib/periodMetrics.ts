/**
 * Utilidades para interpretar métricas de un periodo histórico.
 *
 * Criterio de anualización: siguiendo la práctica de los estándares GIPS
 * (CFA Institute), los rendimientos de periodos menores a un año no deben
 * presentarse anualizados como si fueran representativos. La interfaz los
 * conserva como dato técnico, pero no los destaca.
 */

export const DAYS_PER_YEAR = 365

function parseIsoDate(value: string | null | undefined): Date | null {
  if (typeof value !== 'string' || value.trim() === '') {
    return null
  }

  const date = new Date(`${value.slice(0, 10)}T00:00:00Z`)

  return Number.isNaN(date.getTime()) ? null : date
}

/** Días naturales entre dos fechas ISO (YYYY-MM-DD). */
export function getCalendarDaysBetween(
  startDate: string | null | undefined,
  endDate: string | null | undefined,
): number | null {
  const start = parseIsoDate(startDate)
  const end = parseIsoDate(endDate)

  if (start === null || end === null) {
    return null
  }

  return Math.round((end.getTime() - start.getTime()) / 86_400_000)
}

/** Indica si un periodo es lo bastante largo para mostrar métricas anualizadas. */
export function isAnnualizationRepresentative(
  startDate: string | null | undefined,
  endDate: string | null | undefined,
): boolean {
  const days = getCalendarDaysBetween(startDate, endDate)

  return days !== null && days >= DAYS_PER_YEAR
}

/**
 * Días naturales que el periodo efectivo quedó por debajo del solicitado
 * (al inicio y al final). Devuelve 0 cuando no hay recorte o faltan datos.
 */
export function getPeriodShortfall(params: {
  requestedStart: string | null | undefined
  requestedEnd: string | null | undefined
  effectiveStart: string | null | undefined
  effectiveEnd: string | null | undefined
}): { startDays: number; endDays: number } {
  const startDays = getCalendarDaysBetween(params.requestedStart, params.effectiveStart) ?? 0
  const endDays = getCalendarDaysBetween(params.effectiveEnd, params.requestedEnd) ?? 0

  return {
    startDays: Math.max(startDays, 0),
    endDays: Math.max(endDays, 0),
  }
}
