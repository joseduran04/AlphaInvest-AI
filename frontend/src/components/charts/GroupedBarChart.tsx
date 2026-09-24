import { useState } from 'react'

import { niceDomain, scaleLinear } from '@/lib/chartScales'
import { getFinancialTone } from '@/lib/financialTone'

import { useElementWidth } from './useElementWidth'

export interface GroupedBarItem {
  key: string
  label: string
  /** Monto "antes" (lo invertido o asignado). */
  before: number
  /** Monto "después" (valor actual o final). */
  after: number
  /** Texto del cambio mostrado sobre el grupo, por ejemplo "+2.73 · +0.8 %". */
  changeLabel: string
}

interface GroupedBarChartProps {
  title: string
  description?: string
  beforeLabel: string
  afterLabel: string
  items: GroupedBarItem[]
  formatValue: (value: number) => string
  height?: number
}

const MARGIN = { top: 28, right: 12, bottom: 28, left: 72 }
const BAR_GAP = 2

/**
 * Barras verticales agrupadas "antes y después" por activo. Sobre cada grupo
 * se muestra la ganancia o pérdida (verde/rojo) como texto, así que el color
 * nunca es la única señal. Eje Y desde cero.
 */
export function GroupedBarChart({
  title,
  description,
  beforeLabel,
  afterLabel,
  items,
  formatValue,
  height = 280,
}: GroupedBarChartProps) {
  const { ref, width } = useElementWidth<HTMLDivElement>()
  const [active, setActive] = useState<string | null>(null)

  const innerWidth = Math.max(width - MARGIN.left - MARGIN.right, 60)
  const innerHeight = height - MARGIN.top - MARGIN.bottom

  const { domain, ticks } = niceDomain(
    items.flatMap((item) => [item.before, item.after]),
    { count: 4, includeZero: true },
  )
  const y = scaleLinear(domain, [innerHeight, 0])

  const groupWidth = innerWidth / Math.max(items.length, 1)
  const barWidth = Math.min(Math.max((groupWidth * 0.6 - BAR_GAP) / 2, 6), 48)

  return (
    <figure className="chart">
      <figcaption className="chart__header">
        <strong>{title}</strong>
        {description ? <span className="metric-hint">{description}</span> : null}
      </figcaption>

      <ul className="chart__legend">
        <li>
          <span className="chart__legend-swatch chart__fill-bg--series-1" />
          {beforeLabel}
        </li>
        <li>
          <span className="chart__legend-swatch chart__fill-bg--series-2" />
          {afterLabel}
        </li>
      </ul>

      <div className="chart__canvas" ref={ref}>
        <svg width={width} height={height} role="img" aria-label={title}>
          <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
            {ticks.map((tick) => (
              <g key={tick}>
                <line className="chart__grid" x1={0} x2={innerWidth} y1={y(tick)} y2={y(tick)} />
                <text className="chart__axis-label" x={-8} y={y(tick)} dy="0.32em" textAnchor="end">
                  {formatValue(tick)}
                </text>
              </g>
            ))}

            {items.map((item, index) => {
              const center = groupWidth * index + groupWidth / 2
              const beforeX = center - barWidth - BAR_GAP / 2
              const afterX = center + BAR_GAP / 2
              const tone = getFinancialTone(item.after - item.before)
              const top = Math.min(y(item.before), y(item.after))

              return (
                <g
                  key={item.key}
                  className="chart__bar-group"
                  tabIndex={0}
                  onPointerEnter={() => setActive(item.key)}
                  onPointerLeave={() => setActive(null)}
                  onFocus={() => setActive(item.key)}
                  onBlur={() => setActive(null)}
                >
                  <title>
                    {`${item.label}: ${beforeLabel} ${formatValue(item.before)}, ${afterLabel} ${formatValue(item.after)} (${item.changeLabel})`}
                  </title>

                  <rect
                    className="chart__hit-area"
                    x={groupWidth * index}
                    y={0}
                    width={groupWidth}
                    height={innerHeight}
                  />

                  <rect
                    className="chart__bar chart__fill--series-1"
                    x={beforeX}
                    y={y(item.before)}
                    width={barWidth}
                    height={Math.max(y(0) - y(item.before), 1)}
                    rx={3}
                  />
                  <rect
                    className="chart__bar chart__fill--series-2"
                    x={afterX}
                    y={y(item.after)}
                    width={barWidth}
                    height={Math.max(y(0) - y(item.after), 1)}
                    rx={3}
                  />

                  <text
                    className={`chart__bar-change chart__text--${tone}`}
                    x={center}
                    y={top - 8}
                    textAnchor="middle"
                  >
                    {item.changeLabel}
                  </text>

                  <text
                    className="chart__bar-label"
                    x={center}
                    y={innerHeight + 18}
                    textAnchor="middle"
                  >
                    {item.label}
                  </text>

                  {active === item.key ? (
                    <g className="chart__bar-values">
                      <text x={beforeX + barWidth / 2} y={y(item.before) + 14} textAnchor="middle">
                        {formatValue(item.before)}
                      </text>
                      <text x={afterX + barWidth / 2} y={y(item.after) + 14} textAnchor="middle">
                        {formatValue(item.after)}
                      </text>
                    </g>
                  ) : null}
                </g>
              )
            })}
          </g>
        </svg>
      </div>

      <details className="chart__table">
        <summary>Ver datos en tabla</summary>
        <div className="chart__table-scroll">
          <table>
            <thead>
              <tr>
                <th scope="col">Activo</th>
                <th scope="col">{beforeLabel}</th>
                <th scope="col">{afterLabel}</th>
                <th scope="col">Cambio</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.key}>
                  <th scope="row">{item.label}</th>
                  <td>{formatValue(item.before)}</td>
                  <td>{formatValue(item.after)}</td>
                  <td>{item.changeLabel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </figure>
  )
}
