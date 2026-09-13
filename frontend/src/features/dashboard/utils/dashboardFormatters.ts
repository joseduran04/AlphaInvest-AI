export function formatDashboardLabel(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  return value
    .toLowerCase()
    .split('_')
    .map((word) => `${word.charAt(0).toUpperCase()}${word.slice(1)}`)
    .join(' ')
}

export function formatDashboardDate(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function formatDashboardMoney(value: string | null | undefined, currency: string): string {
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

export function formatDashboardPercentage(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}
