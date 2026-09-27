import { describe, expect, it } from 'vitest'

import {
  buildAssetBreakdown,
  formatSignedCurrency,
  formatSignedPercentage,
} from './simulationBreakdown'

const META = {
  allocatedCapital: '600.00',
  initialPrice: '578.08',
  finalPrice: '751.66',
  initialQuantity: '1.03791191',
  finalQuantity: '1.03791191',
  finalValue: '780.16',
  profitLoss: '180.16',
  contributions: '0',
}

describe('buildAssetBreakdown', () => {
  it('reexpresa el caso META sin comisión ni aportaciones', () => {
    const breakdown = buildAssetBreakdown(META)

    expect(breakdown).not.toBeNull()
    expect(breakdown?.hasCommission).toBe(false)
    expect(breakdown?.hasContributions).toBe(false)
    expect(breakdown?.investedAtStart).toBe(600)
    expect(breakdown?.priceChange).toBeCloseTo(173.58, 2)
    expect(breakdown?.priceChangePercentage).toBeCloseTo(30.03, 2)
    // cambio por acción × acciones = ganancia del backend
    expect((breakdown?.priceChange ?? 0) * (breakdown?.initialQuantity ?? 0)).toBeCloseTo(180.16, 1)
  })

  it('detecta la comisión como diferencia entre lo asignado y lo que compró unidades', () => {
    // 600 con 0.5 % de comisión → neto 597.01
    const quantity = (600 / 1.005 / 578.08).toFixed(8)
    const breakdown = buildAssetBreakdown({ ...META, initialQuantity: quantity })

    expect(breakdown?.hasCommission).toBe(true)
    expect(breakdown?.commission).toBeCloseTo(2.99, 2)
    expect(breakdown?.investedAtStart).toBeCloseTo(597.01, 2)
  })

  it('marca aportaciones cuando existen', () => {
    const breakdown = buildAssetBreakdown({
      ...META,
      contributions: '100.00',
      finalQuantity: '1.2',
    })

    expect(breakdown?.hasContributions).toBe(true)
    expect(breakdown?.finalQuantity).toBe(1.2)
  })

  it('devuelve null si faltan datos', () => {
    expect(buildAssetBreakdown({ ...META, initialPrice: null })).toBeNull()
    expect(buildAssetBreakdown({ ...META, initialPrice: '0' })).toBeNull()
  })
})

describe('formatos con signo', () => {
  it('antepone + o − explícitos', () => {
    expect(formatSignedPercentage(30.0275)).toBe('+30.03 %')
    expect(formatSignedPercentage(-4.1)).toBe('−4.10 %')
    expect(formatSignedCurrency(180.16, 'USD')).toContain('+')
    expect(formatSignedCurrency(-12.4, 'USD').startsWith('−')).toBe(true)
  })
})
