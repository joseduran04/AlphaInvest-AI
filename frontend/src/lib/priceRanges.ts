/** Rangos de tiempo para la gráfica de precio de un activo. */

export const PRICE_RANGES = [
  { key: '1M', label: '1M', months: 1 },
  { key: '3M', label: '3M', months: 3 },
  { key: '6M', label: '6M', months: 6 },
  { key: '1A', label: '1A', months: 12 },
  { key: '5A', label: '5A', months: 60 },
  { key: 'MAX', label: 'Máx', months: null },
] as const

export type PriceRangeKey = (typeof PRICE_RANGES)[number]['key']

/** Fecha ISO de inicio para un rango relativo a hoy (null = todo el histórico). */
export function rangeStartDate(months: number | null, today = new Date()): string | null {
  if (months === null) {
    return null
  }

  const start = new Date(Date.UTC(today.getFullYear(), today.getMonth() - months, today.getDate()))

  return start.toISOString().slice(0, 10)
}
