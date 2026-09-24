/**
 * Traducción de métricas técnicas de IA y noticias a lenguaje comprensible.
 *
 * Reglas:
 * - No se inventan umbrales: solo se traducen etiquetas que ya entrega el
 *   proveedor o el modelo, y se explican fórmulas verificadas en el backend.
 * - "Alcista" describe un sesgo o tono, nunca una garantía de subida.
 */

export type Tone = 'positive' | 'negative' | 'neutral'

/** Con tres clases posibles, una asignación al azar daría 1/3 a cada una. */
export const THREE_CLASS_RANDOM_BASELINE = 1 / 3

export function parseNumber(value: string | number | null | undefined): number | null {
  if (value === null || value === undefined || value === '') {
    return null
  }

  const parsed = Number(value)

  return Number.isFinite(parsed) ? parsed : null
}

/** Probabilidad 0–1 como porcentaje legible ("45 %"). */
export function formatProbabilityPercent(value: string | number | null | undefined): string {
  const parsed = parseNumber(value)

  if (parsed === null) {
    return 'No disponible'
  }

  return `${Math.round(parsed * 100)} %`
}

interface ProviderSentimentLabel {
  text: string
  tone: Tone
}

/**
 * Etiquetas de sentimiento de Alpha Vantage NEWS_SENTIMENT
 * (Bearish, Somewhat-Bearish, Neutral, Somewhat-Bullish, Bullish).
 * Se traducen 1:1; una etiqueta desconocida se muestra tal cual.
 */
const PROVIDER_SENTIMENT_LABELS: Record<string, ProviderSentimentLabel> = {
  bullish: { text: 'Sesgo alcista', tone: 'positive' },
  'somewhat-bullish': { text: 'Sesgo alcista moderado', tone: 'positive' },
  neutral: { text: 'Tono neutral', tone: 'neutral' },
  'somewhat-bearish': { text: 'Sesgo bajista moderado', tone: 'negative' },
  bearish: { text: 'Sesgo bajista', tone: 'negative' },
}

export function translateProviderSentiment(label: string): ProviderSentimentLabel {
  const key = label
    .trim()
    .toLowerCase()
    .replace(/[_\s]+/g, '-')
  const known = PROVIDER_SENTIMENT_LABELS[key]

  if (known) {
    return known
  }

  const tone: Tone = key.includes('bull')
    ? 'positive'
    : key.includes('bear')
      ? 'negative'
      : 'neutral'

  return { text: label, tone }
}

/** Clasificación del modelo de tendencia (ALCISTA / NEUTRAL / BAJISTA). */
export function translateTrend(trend: string): ProviderSentimentLabel {
  switch (trend.trim().toUpperCase()) {
    case 'ALCISTA':
      return { text: 'Sesgo alcista', tone: 'positive' }
    case 'BAJISTA':
      return { text: 'Sesgo bajista', tone: 'negative' }
    case 'NEUTRAL':
      return { text: 'Sin sesgo claro (neutral)', tone: 'neutral' }
    default:
      return { text: trend, tone: 'neutral' }
  }
}

/** Clasificación del modelo de sentimiento (POSITIVO / NEUTRAL / NEGATIVO). */
export function translateSentiment(sentiment: string): ProviderSentimentLabel {
  switch (sentiment.trim().toUpperCase()) {
    case 'POSITIVO':
      return { text: 'Tono positivo', tone: 'positive' }
    case 'NEGATIVO':
      return { text: 'Tono negativo', tone: 'negative' }
    case 'NEUTRAL':
      return { text: 'Tono neutral', tone: 'neutral' }
    default:
      return { text: sentiment, tone: 'neutral' }
  }
}

/**
 * Explica la probabilidad máxima de un clasificador de tres clases
 * comparándola con el azar (33 %). No es una tasa de acierto.
 */
export function describeTopProbability(value: string | number | null | undefined): string {
  const parsed = parseNumber(value)

  if (parsed === null) {
    return 'El modelo no reportó probabilidad.'
  }

  const percent = Math.round(parsed * 100)
  const margin = Math.round((parsed - THREE_CLASS_RANDOM_BASELINE) * 100)

  if (margin <= 0) {
    return `El modelo asigna ${percent} % a esta opción; con tres opciones el azar daría 33 %, así que no hay preferencia real.`
  }

  return `El modelo asigna ${percent} % a esta opción, ${margin} puntos por encima del 33 % que daría el azar con tres opciones. Es la preferencia del modelo, no su tasa de acierto.`
}

/**
 * Relevancia de Alpha Vantage (0 a 1; mayor = el artículo trata más sobre
 * el activo). Se presenta como proporción sin inventar categorías.
 */
export function describeRelevance(value: string | number | null | undefined): string | null {
  const parsed = parseNumber(value)

  if (parsed === null) {
    return null
  }

  return `${Math.round(parsed * 100)} de 100`
}

/**
 * Puntuación del modelo de sentimiento de AlphaInvest:
 * P(positivo) − P(negativo), en el rango de −1 a +1.
 */
export function describeSentimentBalance(params: {
  positive: string | number | null | undefined
  negative: string | number | null | undefined
}): string | null {
  const positive = parseNumber(params.positive)
  const negative = parseNumber(params.negative)

  if (positive === null || negative === null) {
    return null
  }

  const balance = positive - negative
  const sign = balance > 0 ? '+' : ''

  return `Balance ${sign}${balance.toFixed(2)} = ${Math.round(positive * 100)} % positivo − ${Math.round(negative * 100)} % negativo (escala de −1 a +1).`
}
