/** Utilidades de escala para las gráficas SVG de AlphaInvest. */

export interface Domain {
  min: number
  max: number
}

/** Paso "bonito" (1, 2, 2.5, 5 × 10^n) para ~`count` divisiones. */
function niceStep(span: number, count: number): number {
  const raw = span / Math.max(count, 1)
  const magnitude = 10 ** Math.floor(Math.log10(raw))
  const residual = raw / magnitude

  const nice =
    residual <= 1 ? 1 : residual <= 2 ? 2 : residual <= 2.5 ? 2.5 : residual <= 5 ? 5 : 10

  return nice * magnitude
}

/** Dominio redondeado y marcas del eje Y. Incluye el cero si `includeZero`. */
export function niceDomain(
  values: number[],
  { count = 4, includeZero = false }: { count?: number; includeZero?: boolean } = {},
): { domain: Domain; ticks: number[] } {
  const finite = values.filter((value) => Number.isFinite(value))

  let min = finite.length > 0 ? Math.min(...finite) : 0
  let max = finite.length > 0 ? Math.max(...finite) : 1

  if (includeZero) {
    min = Math.min(min, 0)
    max = Math.max(max, 0)
  }

  if (min === max) {
    const pad = Math.abs(min) * 0.05 || 1
    min -= pad
    max += pad
  }

  const step = niceStep(max - min, count)
  const niceMin = Math.floor(min / step) * step
  const niceMax = Math.ceil(max / step) * step

  const ticks: number[] = []

  for (let tick = niceMin; tick <= niceMax + step / 2; tick += step) {
    ticks.push(Number(tick.toFixed(10)))
  }

  return { domain: { min: niceMin, max: niceMax }, ticks }
}

export function scaleLinear(domain: Domain, range: [number, number]) {
  const [r0, r1] = range
  const span = domain.max - domain.min || 1

  return (value: number) => r0 + ((value - domain.min) / span) * (r1 - r0)
}

/** Índices repartidos uniformemente para etiquetar el eje X. */
export function evenlySpacedIndexes(length: number, count: number): number[] {
  if (length <= 0) {
    return []
  }

  if (length <= count) {
    return Array.from({ length }, (_, index) => index)
  }

  const indexes = new Set<number>()

  for (let index = 0; index < count; index += 1) {
    indexes.add(Math.round((index * (length - 1)) / (count - 1)))
  }

  return [...indexes].sort((a, b) => a - b)
}

/** Índice del punto más cercano a una coordenada X (datos ordenados). */
export function nearestIndex(positions: number[], x: number): number {
  let best = 0
  let bestDistance = Number.POSITIVE_INFINITY

  positions.forEach((position, index) => {
    const distance = Math.abs(position - x)

    if (distance < bestDistance) {
      bestDistance = distance
      best = index
    }
  })

  return best
}
