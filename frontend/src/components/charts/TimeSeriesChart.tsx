import { useMemo, useState, type PointerEvent } from 'react'

import { evenlySpacedIndexes, nearestIndex, niceDomain, scaleLinear } from '@/lib/chartScales'

import { useElementWidth } from './useElementWidth'

export interface TimeSeries {
  key: string
  label: string
  /**
   * Rol de color. 'positive'/'negative' solo para una serie única de precio
   * (sube/baja en el periodo, acompañado del cambio en texto).
   */
  color: 'series-1' | 'series-2' | 'muted' | 'positive' | 'negative'
  dashed?: boolean
  values: (number | null)[]
}

interface TimeSeriesChartProps {
  title: string
  description?: string
  /** Fechas ISO (YYYY-MM-DD) compartidas por todas las series. */
  dates: string[]
  series: TimeSeries[]
  formatValue: (value: number) => string
  height?: number
  /** Dibuja una línea de referencia (por ejemplo 0 %). */
  referenceValue?: number
}

const MARGIN = { top: 12, right: 16, bottom: 28, left: 72 }

function formatShortDate(value: string): string {
  const date = new Date(`${value}T00:00:00`)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    day: 'numeric',
    month: 'short',
    year: '2-digit',
  }).format(date)
}

function buildPath(xs: number[], values: (number | null)[], y: (value: number) => number): string {
  let path = ''
  let drawing = false

  values.forEach((value, index) => {
    if (value === null || !Number.isFinite(value)) {
      drawing = false
      return
    }

    path += `${drawing ? 'L' : 'M'}${xs[index].toFixed(1)},${y(value).toFixed(1)}`
    drawing = true
  })

  return path
}

/**
 * Gráfica de líneas en SVG: un solo eje Y, líneas de 2px, cuadrícula tenue,
 * crosshair con tooltip para todas las series, leyenda y tabla de datos.
 */
export function TimeSeriesChart({
  title,
  description,
  dates,
  series,
  formatValue,
  height = 260,
  referenceValue,
}: TimeSeriesChartProps) {
  const { ref, width } = useElementWidth<HTMLDivElement>()
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  const innerWidth = Math.max(width - MARGIN.left - MARGIN.right, 50)
  const innerHeight = height - MARGIN.top - MARGIN.bottom

  const { xs, y, ticks, domain } = useMemo(() => {
    const allValues = series.flatMap((item) =>
      item.values.filter((value): value is number => value !== null),
    )

    if (referenceValue !== undefined) {
      allValues.push(referenceValue)
    }

    const scale = niceDomain(allValues, { count: 4 })
    const xScale = scaleLinear({ min: 0, max: Math.max(dates.length - 1, 1) }, [0, innerWidth])

    return {
      xs: dates.map((_, index) => xScale(index)),
      y: scaleLinear(scale.domain, [innerHeight, 0]),
      ticks: scale.ticks,
      domain: scale.domain,
    }
  }, [dates, innerHeight, innerWidth, referenceValue, series])

  const xLabelIndexes = evenlySpacedIndexes(dates.length, width < 480 ? 3 : 5)

  function handlePointer(event: PointerEvent<SVGRectElement>) {
    const bounds = event.currentTarget.getBoundingClientRect()
    setActiveIndex(nearestIndex(xs, event.clientX - bounds.left))
  }

  const tooltipLeft =
    activeIndex === null ? 0 : Math.min(MARGIN.left + xs[activeIndex] + 12, width - 190)

  return (
    <figure className="chart">
      <figcaption className="chart__header">
        <strong>{title}</strong>
        {description ? <span className="metric-hint">{description}</span> : null}
      </figcaption>

      {series.length > 1 ? (
        <ul className="chart__legend">
          {series.map((item) => (
            <li key={item.key}>
              <span
                className={`chart__legend-line chart__stroke--${item.color}${item.dashed ? ' chart__legend-line--dashed' : ''}`}
              />
              {item.label}
            </li>
          ))}
        </ul>
      ) : null}

      <div className="chart__canvas" ref={ref}>
        <svg
          width={width}
          height={height}
          role="img"
          aria-label={`${title}. ${dates.length} fechas, del ${dates[0] ?? ''} al ${dates.at(-1) ?? ''}.`}
        >
          <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
            {ticks.map((tick) => (
              <g key={tick}>
                <line className="chart__grid" x1={0} x2={innerWidth} y1={y(tick)} y2={y(tick)} />
                <text className="chart__axis-label" x={-8} y={y(tick)} dy="0.32em" textAnchor="end">
                  {formatValue(tick)}
                </text>
              </g>
            ))}

            {referenceValue !== undefined &&
            referenceValue >= domain.min &&
            referenceValue <= domain.max ? (
              <line
                className="chart__reference"
                x1={0}
                x2={innerWidth}
                y1={y(referenceValue)}
                y2={y(referenceValue)}
              />
            ) : null}

            {xLabelIndexes.map((index) => (
              <text
                key={dates[index]}
                className="chart__axis-label"
                x={xs[index]}
                y={innerHeight + 18}
                textAnchor={index === 0 ? 'start' : index === dates.length - 1 ? 'end' : 'middle'}
              >
                {formatShortDate(dates[index])}
              </text>
            ))}

            {series.map((item) => (
              <path
                key={item.key}
                className={`chart__line chart__stroke--${item.color}${item.dashed ? ' chart__line--dashed' : ''}`}
                d={buildPath(xs, item.values, y)}
              />
            ))}

            {activeIndex !== null ? (
              <g>
                <line
                  className="chart__crosshair"
                  x1={xs[activeIndex]}
                  x2={xs[activeIndex]}
                  y1={0}
                  y2={innerHeight}
                />
                {series.map((item) => {
                  const value = item.values[activeIndex]

                  return value === null || !Number.isFinite(value) ? null : (
                    <circle
                      key={item.key}
                      className={`chart__marker chart__fill--${item.color}`}
                      cx={xs[activeIndex]}
                      cy={y(value)}
                      r={4}
                    />
                  )
                })}
              </g>
            ) : null}

            <rect
              className="chart__hit-area"
              width={innerWidth}
              height={innerHeight}
              onPointerMove={handlePointer}
              onPointerDown={handlePointer}
              onPointerLeave={() => setActiveIndex(null)}
            />
          </g>
        </svg>

        {activeIndex !== null ? (
          <div className="chart__tooltip" style={{ left: tooltipLeft }} role="status">
            <span className="chart__tooltip-date">{formatShortDate(dates[activeIndex])}</span>
            {series.map((item) => {
              const value = item.values[activeIndex]

              return (
                <span key={item.key} className="chart__tooltip-row">
                  <span className={`chart__legend-line chart__stroke--${item.color}`} />
                  <strong>
                    {value === null || !Number.isFinite(value) ? '—' : formatValue(value)}
                  </strong>
                  <span>{item.label}</span>
                </span>
              )
            })}
          </div>
        ) : null}
      </div>

      <details className="chart__table">
        <summary>Ver datos en tabla</summary>
        <div className="chart__table-scroll">
          <table>
            <thead>
              <tr>
                <th scope="col">Fecha</th>
                {series.map((item) => (
                  <th key={item.key} scope="col">
                    {item.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dates.map((date, index) => (
                <tr key={date}>
                  <th scope="row">{date}</th>
                  {series.map((item) => {
                    const value = item.values[index]

                    return (
                      <td key={item.key}>
                        {value === null || !Number.isFinite(value) ? '—' : formatValue(value)}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </figure>
  )
}
