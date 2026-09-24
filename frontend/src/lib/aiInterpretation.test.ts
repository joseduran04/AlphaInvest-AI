import { describe, expect, it } from 'vitest'

import {
  describeRelevance,
  describeSentimentBalance,
  describeTopProbability,
  formatProbabilityPercent,
  translateProviderSentiment,
  translateSentiment,
  translateTrend,
} from './aiInterpretation'

describe('translateProviderSentiment', () => {
  it('traduce las etiquetas de Alpha Vantage', () => {
    expect(translateProviderSentiment('Somewhat-Bullish')).toEqual({
      text: 'Sesgo alcista moderado',
      tone: 'positive',
    })
    expect(translateProviderSentiment('Bearish').tone).toBe('negative')
    expect(translateProviderSentiment('Somewhat_Bearish').text).toBe('Sesgo bajista moderado')
    expect(translateProviderSentiment('Neutral').tone).toBe('neutral')
  })

  it('conserva etiquetas desconocidas sin inventar significado', () => {
    expect(translateProviderSentiment('Mixed')).toEqual({ text: 'Mixed', tone: 'neutral' })
  })
})

describe('traducciones de modelos', () => {
  it('traduce tendencia y sentimiento', () => {
    expect(translateTrend('ALCISTA').text).toBe('Sesgo alcista')
    expect(translateTrend('NEUTRAL').tone).toBe('neutral')
    expect(translateSentiment('NEGATIVO')).toEqual({ text: 'Tono negativo', tone: 'negative' })
  })
})

describe('describeTopProbability', () => {
  it('compara contra el azar de tres clases', () => {
    expect(describeTopProbability('0.45')).toContain('12 puntos por encima del 33 %')
    expect(describeTopProbability('0.33')).toContain('no hay preferencia real')
    expect(describeTopProbability(null)).toBe('El modelo no reportó probabilidad.')
  })
})

describe('formatos', () => {
  it('formatea probabilidades y relevancia', () => {
    expect(formatProbabilityPercent('0.4567')).toBe('46 %')
    expect(describeRelevance('0.786')).toBe('79 de 100')
    expect(describeRelevance(null)).toBeNull()
  })

  it('explica el balance de sentimiento', () => {
    expect(describeSentimentBalance({ positive: '0.62', negative: '0.08' })).toBe(
      'Balance +0.54 = 62 % positivo − 8 % negativo (escala de −1 a +1).',
    )
    expect(describeSentimentBalance({ positive: null, negative: '0.1' })).toBeNull()
  })
})
