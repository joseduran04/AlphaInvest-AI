/**
 * Series de rendimiento para gráficas de portafolio y simulación.
 * Todo se calcula a partir de precios de cierre ya guardados.
 */

export interface PositionInput {
  assetId: string
  quantity: number
  cost: number
  /** Fecha de apertura ISO (YYYY-MM-DD). */
  openedOn: string
}

export interface PortfolioSeries {
  dates: string[]
  invested: (number | null)[]
  value: (number | null)[]
  /** Rendimiento acumulado del portafolio sobre lo invertido, en %. */
  returnPercentage: (number | null)[]
}

/** Unión ordenada de fechas con precio, desde `startDate`. */
export function unionDates(closes: Map<string, number>[], startDate: string): string[] {
  const dates = new Set<string>()

  closes.forEach((series) => {
    series.forEach((_, date) => {
      if (date >= startDate) {
        dates.add(date)
      }
    })
  })

  return [...dates].sort()
}

/** Último precio conocido en o antes de `date` (arrastra fines de semana). */
function priceOnOrBefore(sortedDates: string[], closes: Map<string, number>, date: string) {
  let low = 0
  let high = sortedDates.length - 1
  let found = -1

  while (low <= high) {
    const middle = (low + high) >> 1

    if (sortedDates[middle] <= date) {
      found = middle
      low = middle + 1
    } else {
      high = middle - 1
    }
  }

  return found === -1 ? null : (closes.get(sortedDates[found]) ?? null)
}

/**
 * Reconstruye la evolución diaria del portafolio: cada posición cuenta desde
 * su fecha de apertura con su cantidad actual.
 */
export function buildPortfolioSeries(
  positions: PositionInput[],
  closesByAsset: Map<string, Map<string, number>>,
): PortfolioSeries {
  if (positions.length === 0) {
    return { dates: [], invested: [], value: [], returnPercentage: [] }
  }

  const startDate = positions.map((position) => position.openedOn).sort()[0]
  const dates = unionDates([...closesByAsset.values()], startDate)
  const sortedByAsset = new Map(
    [...closesByAsset.entries()].map(([assetId, closes]) => [assetId, [...closes.keys()].sort()]),
  )

  const invested: (number | null)[] = []
  const value: (number | null)[] = []
  const returnPercentage: (number | null)[] = []

  for (const date of dates) {
    let investedToday = 0
    let valueToday = 0
    let complete = true

    for (const position of positions) {
      if (position.openedOn > date) {
        continue
      }

      const closes = closesByAsset.get(position.assetId)
      const price = closes
        ? priceOnOrBefore(sortedByAsset.get(position.assetId) ?? [], closes, date)
        : null

      investedToday += position.cost

      if (price === null) {
        complete = false
        continue
      }

      valueToday += position.quantity * price
    }

    invested.push(investedToday > 0 ? investedToday : null)
    value.push(investedToday > 0 && complete ? valueToday : null)
    returnPercentage.push(
      investedToday > 0 && complete ? (valueToday / investedToday - 1) * 100 : null,
    )
  }

  return { dates, invested, value, returnPercentage }
}

/** Rendimiento acumulado (%) de una referencia desde la primera fecha. */
export function benchmarkReturn(dates: string[], closes: Map<string, number>): (number | null)[] {
  const sortedDates = [...closes.keys()].sort()
  const base = dates.length > 0 ? priceOnOrBefore(sortedDates, closes, dates[0]) : null

  return dates.map((date) => {
    const price = priceOnOrBefore(sortedDates, closes, date)

    return base === null || price === null ? null : (price / base - 1) * 100
  })
}
