import { formatProbabilityPercent, parseNumber, type Tone } from '@/lib/aiInterpretation'

export interface ProbabilityBarItem {
  label: string
  value: string | number | null | undefined
  tone: Tone
}

interface ProbabilityBarsProps {
  title: string
  items: ProbabilityBarItem[]
}

/** Barras horizontales accesibles para probabilidades 0–1. */
export function ProbabilityBars({ title, items }: ProbabilityBarsProps) {
  return (
    <div className="probability-bars">
      <h3>{title}</h3>

      <ul>
        {items.map((item) => {
          const parsed = parseNumber(item.value)
          const percent = parsed === null ? 0 : Math.max(0, Math.min(100, parsed * 100))

          return (
            <li key={item.label}>
              <span className="probability-bars__label">{item.label}</span>

              <span
                className="probability-bars__track"
                role="meter"
                aria-label={item.label}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={Math.round(percent)}
              >
                <span
                  className={`probability-bars__fill probability-bars__fill--${item.tone}`}
                  style={{ width: `${percent}%` }}
                />
              </span>

              <span className="probability-bars__value">
                {formatProbabilityPercent(item.value)}
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
