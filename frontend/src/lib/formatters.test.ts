import { describe, expect, it } from 'vitest'

import { formatCurrency } from './formatters'

describe('formatCurrency', () => {
  it('devuelve No disponible para null y undefined', () => {
    expect(formatCurrency(null, 'MXN')).toBe('No disponible')
    expect(formatCurrency(undefined, 'MXN')).toBe('No disponible')
  })

  it('formatea valores numéricos como moneda', () => {
    const result = formatCurrency(1234.5, 'MXN')

    expect(result).toContain('1,234.50')
    expect(result).toContain('$')
  })

  it('acepta valores numéricos recibidos como string', () => {
    const result = formatCurrency('2500.25', 'USD')

    expect(result).toContain('2,500.25')
  })

  it('conserva un valor no numérico junto con su moneda', () => {
    expect(formatCurrency('desconocido', 'MXN')).toBe('desconocido MXN')
  })

  it('utiliza el fallback cuando el código de moneda no es válido', () => {
    expect(formatCurrency(100, 'INVALID_CURRENCY')).toBe('100.00 INVALID_CURRENCY')
  })
})
