import type { AssetResponse, SimulationAssetResultResponse } from '@/api/types'
import { formatCurrency } from '@/lib/formatters'

interface SimulationAllocationProps {
  assets: SimulationAssetResultResponse[]
  marketAssetsById: Map<string, AssetResponse>
  currency: string
  initialCapital: string
}

function toPercentage(value: string): number {
  const parsed = Number(value)

  return Number.isFinite(parsed) ? Math.min(100, Math.max(0, parsed)) : 0
}

/** Cómo se repartió el capital inicial entre los activos (% y monto). */
export function SimulationAllocation({
  assets,
  marketAssetsById,
  currency,
  initialCapital,
}: SimulationAllocationProps) {
  if (assets.length === 0) {
    return null
  }

  return (
    <div className="simulation-result-subsection">
      <h4>Cómo se repartió tu capital</h4>
      <p className="metric-hint">
        {`El capital inicial de ${formatCurrency(initialCapital, currency)} se divide según el porcentaje de cada activo. Ese monto es el "capital asignado" con el que se compra el activo el primer día.`}
      </p>

      <ul className="allocation-bars">
        {assets.map((asset) => {
          const percentage = toPercentage(asset.porcentaje_asignado)
          const symbol = marketAssetsById.get(asset.activo_id)?.symbol ?? 'Activo'

          return (
            <li key={asset.id} className="allocation-bars__row">
              <span className="allocation-bars__label">{symbol}</span>
              <span className="allocation-bars__track" aria-hidden="true">
                <span className="allocation-bars__fill" style={{ width: `${percentage}%` }} />
              </span>
              <span className="allocation-bars__value">
                <strong>{`${percentage.toFixed(2)} %`}</strong>
                <span>{formatCurrency(asset.capital_asignado, currency)}</span>
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
