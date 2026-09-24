import { describe, expect, it } from 'vitest'

import { getFinancialTone, getFinancialToneClass } from './financialTone'

describe('getFinancialTone', () => {
  it('clasifica valores positivos, negativos y cero', () => {
    expect(getFinancialTone('2.73')).toBe('positive')
    expect(getFinancialTone(-0.01)).toBe('negative')
    expect(getFinancialTone('0')).toBe('neutral')
    expect(getFinancialTone('0.00000000')).toBe('neutral')
  })

  it('trata valores ausentes o no numéricos como neutrales', () => {
    expect(getFinancialTone(null)).toBe('neutral')
    expect(getFinancialTone(undefined)).toBe('neutral')
    expect(getFinancialTone('')).toBe('neutral')
    expect(getFinancialTone('abc')).toBe('neutral')
  })

  it('devuelve la clase CSS correspondiente', () => {
    expect(getFinancialToneClass('-5')).toBe('financial-value financial-value--negative')
  })
})
