export type FinancialTone = 'positive' | 'negative' | 'neutral'

/**
 * Clasifica un valor monetario o porcentual para colorearlo de forma
 * consistente: positivo → verde, negativo → rojo, cero o sin dato → neutral.
 */
export function getFinancialTone(value: string | number | null | undefined): FinancialTone {
  if (value === null || value === undefined || value === '') {
    return 'neutral'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue) || parsedValue === 0) {
    return 'neutral'
  }

  return parsedValue > 0 ? 'positive' : 'negative'
}

/** Clase CSS del design system asociada al signo del valor. */
export function getFinancialToneClass(value: string | number | null | undefined): string {
  return `financial-value financial-value--${getFinancialTone(value)}`
}
