export function formatCurrency(
  value: string | number | null | undefined,
  currency: string,
): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return `${value} ${currency}`
  }

  try {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency,
    }).format(parsedValue)
  } catch {
    return `${parsedValue.toFixed(2)} ${currency}`
  }
}
