/**
 * Desglose explicativo del resultado de un activo en una simulación.
 *
 * No introduce cálculos financieros nuevos: reexpresa los datos que ya
 * entrega el backend (capital asignado, precios, cantidades, valor final
 * y ganancia) para mostrar al usuario de dónde sale cada cifra.
 */

/** Diferencias menores a medio centavo se consideran redondeo, no comisión. */
const COMMISSION_EPSILON = 0.005

export interface AssetBreakdownInput {
  allocatedCapital: string | null | undefined
  initialPrice: string | null | undefined
  finalPrice: string | null | undefined
  initialQuantity: string | null | undefined
  finalQuantity: string | null | undefined
  finalValue: string | null | undefined
  profitLoss: string | null | undefined
  contributions: string | null | undefined
}

export interface AssetBreakdown {
  allocatedCapital: number
  initialPrice: number
  finalPrice: number
  initialQuantity: number
  finalQuantity: number
  finalValue: number
  profitLoss: number
  contributions: number
  /** Parte del capital asignado que se fue en comisión de compra. */
  commission: number
  /** Dinero que realmente compró acciones al inicio. */
  investedAtStart: number
  /** Cambio de precio de una sola unidad (acción, moneda, etc.). */
  priceChange: number
  priceChangePercentage: number | null
  hasCommission: boolean
  hasContributions: boolean
}

function toNumber(value: string | null | undefined): number | null {
  if (value === null || value === undefined || value.trim() === '') {
    return null
  }

  const parsed = Number(value)

  return Number.isFinite(parsed) ? parsed : null
}

export function buildAssetBreakdown(input: AssetBreakdownInput): AssetBreakdown | null {
  const allocatedCapital = toNumber(input.allocatedCapital)
  const initialPrice = toNumber(input.initialPrice)
  const finalPrice = toNumber(input.finalPrice)
  const initialQuantity = toNumber(input.initialQuantity)
  const finalValue = toNumber(input.finalValue)
  const profitLoss = toNumber(input.profitLoss)

  if (
    allocatedCapital === null ||
    initialPrice === null ||
    finalPrice === null ||
    initialQuantity === null ||
    finalValue === null ||
    profitLoss === null ||
    initialPrice <= 0
  ) {
    return null
  }

  const finalQuantity = toNumber(input.finalQuantity) ?? initialQuantity
  const contributions = Math.max(0, toNumber(input.contributions) ?? 0)

  const investedAtStart = initialQuantity * initialPrice
  const rawCommission = allocatedCapital - investedAtStart
  const hasCommission = rawCommission >= COMMISSION_EPSILON
  const commission = hasCommission ? rawCommission : 0

  const priceChange = finalPrice - initialPrice

  return {
    allocatedCapital,
    initialPrice,
    finalPrice,
    initialQuantity,
    finalQuantity,
    finalValue,
    profitLoss,
    contributions,
    commission,
    investedAtStart: hasCommission ? investedAtStart : allocatedCapital,
    priceChange,
    priceChangePercentage: (priceChange / initialPrice) * 100,
    hasCommission,
    hasContributions: contributions >= COMMISSION_EPSILON,
  }
}

/** Cantidad de unidades con hasta 4 decimales (1.0379 acciones). */
export function formatQuantity(value: number, maximumFractionDigits = 4): string {
  return new Intl.NumberFormat('es-MX', {
    minimumFractionDigits: 0,
    maximumFractionDigits,
  }).format(value)
}

/** Porcentaje con signo explícito: +30.03 %, −4.10 %. */
export function formatSignedPercentage(value: number | null): string {
  if (value === null || !Number.isFinite(value)) {
    return 'No disponible'
  }

  const sign = value > 0 ? '+' : value < 0 ? '−' : ''

  return `${sign}${Math.abs(value).toFixed(2)} %`
}

/** Monto con signo explícito: +USD 180.16, −USD 12.40. */
export function formatSignedCurrency(value: number, currency: string): string {
  const absolute = new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency,
  }).format(Math.abs(value))

  if (value > 0) {
    return `+${absolute}`
  }

  return value < 0 ? `−${absolute}` : absolute
}
