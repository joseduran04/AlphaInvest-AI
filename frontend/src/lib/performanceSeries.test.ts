import { describe, expect, it } from 'vitest'

import { benchmarkReturn, buildPortfolioSeries } from './performanceSeries'

const aapl = new Map([
  ['2026-09-21', 338.98],
  ['2026-09-22', 339.75],
  ['2026-09-23', 337.02],
])

const nvda = new Map([
  ['2026-09-22', 220.0],
  ['2026-09-23', 218.29],
])

describe('buildPortfolioSeries', () => {
  it('suma cada posición desde su apertura', () => {
    const series = buildPortfolioSeries(
      [
        { assetId: 'aapl', quantity: 1, cost: 337.02, openedOn: '2026-09-21' },
        { assetId: 'nvda', quantity: 1, cost: 225.51, openedOn: '2026-09-22' },
      ],
      new Map([
        ['aapl', aapl],
        ['nvda', nvda],
      ]),
    )

    expect(series.dates).toEqual(['2026-09-21', '2026-09-22', '2026-09-23'])
    expect(series.invested).toEqual([337.02, 562.53, 562.53])
    expect(series.value[0]).toBeCloseTo(338.98)
    expect(series.value[2]).toBeCloseTo(555.31)
    expect(series.returnPercentage[2]).toBeCloseTo((555.31 / 562.53 - 1) * 100)
  })

  it('devuelve series vacías sin posiciones', () => {
    expect(buildPortfolioSeries([], new Map()).dates).toEqual([])
  })
})

describe('benchmarkReturn', () => {
  it('calcula el rendimiento acumulado desde la primera fecha', () => {
    const result = benchmarkReturn(['2026-09-21', '2026-09-23'], aapl)

    expect(result[0]).toBe(0)
    expect(result[1]).toBeCloseTo((337.02 / 338.98 - 1) * 100)
  })

  it('arrastra el último precio en fechas sin cotización', () => {
    const result = benchmarkReturn(['2026-09-22', '2026-09-24'], nvda)

    expect(result[1]).toBeCloseTo((218.29 / 220 - 1) * 100)
  })
})
