import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import type { AssetResponse } from '@/api/types'
import { synchronizeAssetPricesRequest } from '@/features/market/api/marketApi'
import { useAssets } from '@/features/market/hooks/useAssets'

interface SyncFailure {
  symbol: string
  message: string
}

type SyncState =
  | { status: 'idle' }
  | { status: 'running'; current: number; total: number; symbol: string }
  | { status: 'done'; total: number; failures: SyncFailure[] }

/**
 * Sincroniza los precios de todos los activos ACTIVO, uno por uno, reutilizando
 * el endpoint de sincronización por activo. Muestra el avance y los errores.
 */
export function SyncAllPricesPanel() {
  const queryClient = useQueryClient()
  const assetsQuery = useAssets({ status: 'ACTIVO', limit: 100, offset: 0 })
  const [state, setState] = useState<SyncState>({ status: 'idle' })

  async function synchronizeAll(assets: AssetResponse[]) {
    const failures: SyncFailure[] = []

    for (const [index, asset] of assets.entries()) {
      setState({
        status: 'running',
        current: index + 1,
        total: assets.length,
        symbol: asset.symbol,
      })

      try {
        await synchronizeAssetPricesRequest(asset.id)
      } catch (error) {
        failures.push({
          symbol: asset.symbol,
          message: error instanceof Error ? error.message : 'Error desconocido',
        })
      }
    }

    setState({ status: 'done', total: assets.length, failures })

    // Precios, posiciones, dashboard y gráficas dependen de los precios nuevos.
    await queryClient.invalidateQueries()
  }

  const assets = assetsQuery.data?.items ?? []
  const isRunning = state.status === 'running'

  return (
    <div className="market-sync-all">
      <button
        className="button button--primary"
        type="button"
        disabled={isRunning || assets.length === 0}
        onClick={() => {
          void synchronizeAll(assets)
        }}
      >
        {isRunning ? 'Sincronizando...' : 'Sincronizar todos los precios'}
      </button>

      {state.status === 'running' ? (
        <p className="metric-hint" role="status">
          Sincronizando {state.current} de {state.total}: {state.symbol}
          <progress value={state.current - 1} max={state.total} />
        </p>
      ) : null}

      {state.status === 'done' ? (
        state.failures.length === 0 ? (
          <p className="metric-hint" role="status">
            Listo: {state.total} activos actualizados al día de hoy.
          </p>
        ) : (
          <div className="notice notice--warning" role="status">
            <strong>
              {state.total - state.failures.length} de {state.total} activos actualizados.
            </strong>
            <ul>
              {state.failures.map((failure) => (
                <li key={failure.symbol}>
                  {failure.symbol}: {failure.message}
                </li>
              ))}
            </ul>
          </div>
        )
      ) : null}
    </div>
  )
}
