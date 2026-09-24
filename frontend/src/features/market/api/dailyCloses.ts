import type { HistoricalPriceResponse } from '@/api/types'
import { historicalPricesRequest } from '@/features/market/api/marketApi'

/** Fuente preferida cuando hay varias para la misma fecha (trae cierre ajustado). */
const PREFERRED_SOURCE = 'Yahoo Finance'
const PAGE_SIZE = 500
const MAX_PAGES = 12

function priceOf(item: HistoricalPriceResponse): number {
  return Number(item.adjusted_close ?? item.close)
}

/**
 * Elige un precio por fecha cuando hay varias fuentes: primero la preferida,
 * luego la que trae cierre ajustado.
 */
export function pickDailyCloses(items: HistoricalPriceResponse[]): Map<string, number> {
  const chosen = new Map<string, HistoricalPriceResponse>()

  for (const item of items) {
    const current = chosen.get(item.date)

    const isBetter =
      current === undefined ||
      (item.source.name === PREFERRED_SOURCE && current.source.name !== PREFERRED_SOURCE) ||
      (item.source.name === current.source.name &&
        item.adjusted_close != null &&
        current.adjusted_close == null)

    if (isBetter) {
      chosen.set(item.date, item)
    }
  }

  const closes = new Map<string, number>()

  ;[...chosen.keys()].sort().forEach((date) => {
    const price = priceOf(chosen.get(date)!)

    if (Number.isFinite(price) && price > 0) {
      closes.set(date, price)
    }
  })

  return closes
}

/** Cierres diarios (ordenados por fecha) de un activo desde `startDate`. */
export async function fetchDailyCloses(
  assetId: string,
  startDate: string,
  endDate?: string,
): Promise<Map<string, number>> {
  const items: HistoricalPriceResponse[] = []

  for (let page = 0; page < MAX_PAGES; page += 1) {
    const response = await historicalPricesRequest(assetId, {
      start_date: startDate,
      end_date: endDate,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    })

    items.push(...response.items)

    if (items.length >= response.total || response.items.length === 0) {
      break
    }
  }

  return pickDailyCloses(items)
}
