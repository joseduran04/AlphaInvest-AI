import { niceDomain, scaleLinear } from '@/lib/chartScales'

import { useElementWidth } from './useElementWidth'

export interface DivergingBarItem {
  key: string
  label: string
  value: number
  /** Texto secundario (por ejemplo, el rendimiento en %). */
  detail?: string
}

interface DivergingBarChartProps {
  title: string
  description?: string
  items: DivergingBarItem[]
  formatValue: (value: number) => string
}

const LABEL_WIDTH = 72
const VALUE_WIDTH = 120
const BAR_HEIGHT = 20
const ROW_GAP = 10

/**
 * Barras horizontales alrededor de cero: ganancias en verde a la derecha y
 * pérdidas en rojo a la izquierda. Cada barra lleva su valor como texto, así
 * que el color nunca es la única señal.
 */
export function DivergingBarChart({
  title,
  description,
  items,
  formatValue,
}: DivergingBarChartProps) {
  const { ref, width } = useElementWidth<HTMLDivElement>()

  const plotWidth = Math.max(width - LABEL_WIDTH - VALUE_WIDTH, 60)
  const { domain } = niceDomain(
    items.map((item) => item.value),
    { count: 4, includeZero: true },
  )
  const x = scaleLinear(domain, [0, plotWidth])
  const zero = x(0)
  const height = items.length * (BAR_HEIGHT + ROW_GAP) + ROW_GAP

  return (
    <figure className="chart">
      <figcaption className="chart__header">
        <strong>{title}</strong>
        {description ? <span className="metric-hint">{description}</span> : null}
      </figcaption>

      <div className="chart__canvas" ref={ref}>
        <svg width={width} height={height} role="img" aria-label={title}>
          <line
            className="chart__reference"
            x1={LABEL_WIDTH + zero}
            x2={LABEL_WIDTH + zero}
            y1={0}
            y2={height}
          />

          {items.map((item, index) => {
            const top = ROW_GAP + index * (BAR_HEIGHT + ROW_GAP)
            const barX = Math.min(x(item.value), zero)
            const barWidth = Math.max(Math.abs(x(item.value) - zero), 2)
            const tone = item.value > 0 ? 'positive' : item.value < 0 ? 'negative' : 'muted'

            return (
              <g key={item.key} tabIndex={0} className="chart__bar-row">
                <title>
                  {`${item.label}: ${formatValue(item.value)}${item.detail ? ` (${item.detail})` : ''}`}
                </title>
                <text
                  className="chart__bar-label"
                  x={LABEL_WIDTH - 8}
                  y={top + BAR_HEIGHT / 2}
                  dy="0.32em"
                  textAnchor="end"
                >
                  {item.label}
                </text>
                <rect
                  className={`chart__bar chart__fill--${tone}`}
                  x={LABEL_WIDTH + barX}
                  y={top}
                  width={barWidth}
                  height={BAR_HEIGHT}
                  rx={4}
                />
                <text
                  className="chart__bar-value"
                  x={LABEL_WIDTH + plotWidth + 8}
                  y={top + BAR_HEIGHT / 2}
                  dy="0.32em"
                >
                  {formatValue(item.value)}
                  {item.detail ? ` · ${item.detail}` : ''}
                </text>
              </g>
            )
          })}
        </svg>
      </div>
    </figure>
  )
}
