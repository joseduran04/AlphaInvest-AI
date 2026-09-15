import { useMemo, useState } from 'react'

import type { SimulationConfigurationStatus } from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAssets } from '@/features/market/hooks/useAssets'
import { AddSimulationAssetForm } from '@/features/simulation/components/AddSimulationAssetForm'
import { SimulationAssetItem } from '@/features/simulation/components/SimulationAssetItem'
import { useSimulationConfigurationAssets } from '@/features/simulation/hooks/useSimulationConfigurationAssets'
import { useSimulationDistribution } from '@/features/simulation/hooks/useSimulationDistribution'
import { formatCurrency } from '@/lib/formatters'

interface SimulationAssetsSectionProps {
  configurationId: string
  status: SimulationConfigurationStatus
  currency: string
  canUpdate: boolean
}

function formatPercentage(value: string): string {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}

export function SimulationAssetsSection({
  configurationId,
  status,
  currency,
  canUpdate,
}: SimulationAssetsSectionProps) {
  const [showAddForm, setShowAddForm] = useState(false)

  const isDraft = status === 'BORRADOR'
  const canManage = canUpdate && isDraft

  const assetsQuery = useSimulationConfigurationAssets(configurationId)
  const distributionQuery = useSimulationDistribution(configurationId)

  const marketAssetsQuery = useAssets({
    status: 'ACTIVO',
    limit: 100,
    offset: 0,
  })

  const marketAssetsById = useMemo(
    () => new Map((marketAssetsQuery.data?.items ?? []).map((asset) => [asset.id, asset])),
    [marketAssetsQuery.data?.items],
  )

  const configuredAssetIds = useMemo(
    () => new Set((assetsQuery.data?.items ?? []).map((asset) => asset.activo_id)),
    [assetsQuery.data?.items],
  )

  if (assetsQuery.isPending || distributionQuery.isPending) {
    return (
      <section className="simulation-detail-section">
        <PageLoadingState message="Cargando activos y distribución..." />
      </section>
    )
  }

  if (assetsQuery.isError) {
    return (
      <section className="simulation-detail-section">
        <PageErrorState
          title="No fue posible cargar los activos"
          message={assetsQuery.error.message}
          onRetry={() => {
            void assetsQuery.refetch()
          }}
        />
      </section>
    )
  }

  if (distributionQuery.isError) {
    return (
      <section className="simulation-detail-section">
        <PageErrorState
          title="No fue posible cargar la distribución"
          message={distributionQuery.error.message}
          onRetry={() => {
            void distributionQuery.refetch()
          }}
        />
      </section>
    )
  }

  const configuredAssets = assetsQuery.data.items
  const distribution = distributionQuery.data

  return (
    <section className="simulation-detail-section">
      <header className="simulation-detail-section__header">
        <div>
          <p className="simulation-results__eyebrow">Composición</p>
          <h2>Activos y distribución</h2>
          <p>
            Administra los activos que forman parte de la simulación y consulta la distribución
            calculada por el backend.
          </p>
        </div>

        {canManage && !showAddForm ? (
          <button
            className="button button--secondary"
            type="button"
            onClick={() => setShowAddForm(true)}
          >
            Agregar activo
          </button>
        ) : null}
      </header>

      <dl className="simulation-distribution-summary">
        <div>
          <dt>Activos</dt>
          <dd>{distribution.cantidad_activos}</dd>
        </div>

        <div>
          <dt>Porcentaje total</dt>
          <dd>{formatPercentage(distribution.porcentaje_total)}</dd>
        </div>

        <div>
          <dt>Monto total</dt>
          <dd>{formatCurrency(distribution.monto_total, currency)}</dd>
        </div>

        <div>
          <dt>Distribución</dt>
          <dd>
            <span
              className={`simulation-distribution-status ${
                distribution.distribucion_valida
                  ? 'simulation-distribution-status--valid'
                  : 'simulation-distribution-status--invalid'
              }`}
            >
              {distribution.distribucion_valida ? 'Válida' : 'Incompleta'}
            </span>
          </dd>
        </div>
      </dl>

      {showAddForm && canManage ? (
        <AddSimulationAssetForm
          configurationId={configurationId}
          marketAssets={marketAssetsQuery.data?.items ?? []}
          configuredAssetIds={configuredAssetIds}
          nextOrder={configuredAssets.length + 1}
          isMarketLoading={marketAssetsQuery.isPending}
          marketError={marketAssetsQuery.isError ? marketAssetsQuery.error.message : null}
          onCancel={() => setShowAddForm(false)}
          onAdded={() => setShowAddForm(false)}
        />
      ) : null}

      {configuredAssets.length === 0 ? (
        <div className="simulation-assets-empty">
          <strong>No hay activos configurados.</strong>
          <span>
            {canManage
              ? 'Agrega al menos un activo para comenzar a construir la distribución.'
              : 'Esta configuración no tiene activos registrados.'}
          </span>
        </div>
      ) : (
        <div className="simulation-assets-list">
          {configuredAssets.map((configuredAsset) => (
            <SimulationAssetItem
              key={configuredAsset.activo_id}
              configurationId={configurationId}
              configuredAsset={configuredAsset}
              marketAsset={marketAssetsById.get(configuredAsset.activo_id)}
              currency={currency}
              canManage={canManage}
            />
          ))}
        </div>
      )}
    </section>
  )
}
