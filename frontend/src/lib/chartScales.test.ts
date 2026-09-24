import { describe, expect, it } from 'vitest'

import { evenlySpacedIndexes, nearestIndex, niceDomain, scaleLinear } from './chartScales'

describe('niceDomain', () => {
  it('redondea el dominio a pasos legibles', () => {
    const { domain, ticks } = niceDomain([9437.47, 10558.04])

    expect(domain.min).toBeLessThanOrEqual(9437.47)
    expect(domain.max).toBeGreaterThanOrEqual(10558.04)
    expect(ticks[0]).toBe(domain.min)
    expect(ticks.at(-1)).toBe(domain.max)
  })

  it('incluye el cero para barras', () => {
    const { domain } = niceDomain([-7.22, 2.73], { includeZero: true })

    expect(domain.min).toBeLessThan(0)
    expect(domain.max).toBeGreaterThan(0)
  })

  it('maneja series planas', () => {
    const { domain } = niceDomain([100, 100])

    expect(domain.max).toBeGreaterThan(domain.min)
  })
})

describe('escalas', () => {
  it('mapea valores al rango', () => {
    const scale = scaleLinear({ min: 0, max: 10 }, [0, 100])

    expect(scale(5)).toBe(50)
  })

  it('reparte etiquetas y encuentra el punto más cercano', () => {
    expect(evenlySpacedIndexes(10, 3)).toEqual([0, 5, 9])
    expect(evenlySpacedIndexes(2, 5)).toEqual([0, 1])
    expect(nearestIndex([0, 10, 20], 14)).toBe(1)
  })
})
