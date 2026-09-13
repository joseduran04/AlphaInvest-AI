import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type { AssetListQuery, AssetStatus } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useAssets } from '@/features/market/hooks/useAssets'
import { useAssetTypes } from '@/features/market/hooks/useAssetTypes'
import { useMarkets } from '@/features/market/hooks/useMarkets'

import '@/styles/market.css'

const PAGE_SIZE = 20

interface MarketFilters {
  search: string
  marketCode: string
  assetTypeCode: string
  sector: string
  currency: string
  status: AssetStatus | ''
}

const initialFilters: MarketFilters = {
  search: '',
  marketCode: '',
  assetTypeCode: '',
  sector: '',
  currency: '',
  status: '',
}

function formatAssetStatus(status: AssetStatus): string {
  switch (status) {
    case 'ACTIVO':
      return 'Activo'
    case 'INACTIVO':
      return 'Inactivo'
    case 'SUSPENDIDO':
      return 'Suspendido'
  }
}

export function MarketPage() {
  const { hasPermission } = useAuth()

  const canReadAssets = hasPermission('activos.leer')

  const [draftFilters, setDraftFilters] = useState<MarketFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<MarketFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const params: AssetListQuery = {
    search: appliedFilters.search || undefined,
    market_code: appliedFilters.marketCode || undefined,
    asset_type_code: appliedFilters.assetTypeCode || undefined,
    sector: appliedFilters.sector || undefined,
    currency: appliedFilters.currency || undefined,
    status: appliedFilters.status || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const assetsQuery = useAssets(params, canReadAssets)
  const marketsQuery = useMarkets({}, canReadAssets)
  const assetTypesQuery = useAssetTypes({}, canReadAssets)

  if (!canReadAssets) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar activos de mercado."
      />
    )
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setAppliedFilters({
      ...draftFilters,
      search: draftFilters.search.trim(),
      sector: draftFilters.sector.trim(),
      currency: draftFilters.currency.trim().toUpperCase(),
    })
    setPage(0)
  }

  function handleReset() {
    setDraftFilters(initialFilters)
    setAppliedFilters(initialFilters)
    setPage(0)
  }

  const assets = assetsQuery.data?.items ?? []
  const total = assetsQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const firstResult = total === 0 ? 0 : page * PAGE_SIZE + 1
  const lastResult = Math.min((page + 1) * PAGE_SIZE, total)

  return (
    <section className="market-page">
      <header className="market-page__header">
        <div>
          <p className="app__eyebrow">Mercado</p>
          <h1>Explorador de activos</h1>
          <p className="app__description">
            Consulta los instrumentos financieros disponibles y filtra el catálogo de acuerdo con la
            información registrada en AlphaInvest AI.
          </p>
        </div>
      </header>

      <form className="market-filters" onSubmit={handleSubmit}>
        <div className="market-filters__header">
          <div>
            <h2>Filtros</h2>
            <p>Refina la consulta utilizando los criterios disponibles en el mercado.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="market-filters__grid">
          <label className="market-field market-field--wide">
            <span>Buscar</span>
            <input
              type="search"
              value={draftFilters.search}
              maxLength={200}
              placeholder="Símbolo o nombre"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  search: event.target.value,
                }))
              }
            />
          </label>

          <label className="market-field">
            <span>Mercado</span>
            <select
              value={draftFilters.marketCode}
              disabled={marketsQuery.isPending || marketsQuery.isError}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  marketCode: event.target.value,
                }))
              }
            >
              <option value="">Todos</option>

              {marketsQuery.data?.items.map((market) => (
                <option key={market.id} value={market.code}>
                  {market.name}
                </option>
              ))}
            </select>
          </label>

          <label className="market-field">
            <span>Tipo de activo</span>
            <select
              value={draftFilters.assetTypeCode}
              disabled={assetTypesQuery.isPending || assetTypesQuery.isError}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  assetTypeCode: event.target.value,
                }))
              }
            >
              <option value="">Todos</option>

              {assetTypesQuery.data?.items.map((assetType) => (
                <option key={assetType.id} value={assetType.code}>
                  {assetType.name}
                </option>
              ))}
            </select>
          </label>

          <label className="market-field">
            <span>Sector</span>
            <input
              type="text"
              value={draftFilters.sector}
              maxLength={100}
              placeholder="Ej. Tecnología"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  sector: event.target.value,
                }))
              }
            />
          </label>

          <label className="market-field">
            <span>Moneda</span>
            <input
              type="text"
              value={draftFilters.currency}
              maxLength={3}
              pattern="[A-Za-z]{3}"
              placeholder="USD"
              title="Introduce un código de moneda de tres letras"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  currency: event.target.value,
                }))
              }
            />
          </label>

          <label className="market-field">
            <span>Estado</span>
            <select
              value={draftFilters.status}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  status: event.target.value as AssetStatus | '',
                }))
              }
            >
              <option value="">Todos</option>
              <option value="ACTIVO">Activo</option>
              <option value="INACTIVO">Inactivo</option>
              <option value="SUSPENDIDO">Suspendido</option>
            </select>
          </label>
        </div>

        <div className="market-filters__actions">
          <button className="button button--primary" type="submit">
            Aplicar filtros
          </button>
        </div>
      </form>

      <section className="market-results">
        <header className="market-results__header">
          <div>
            <p className="market-results__eyebrow">Resultados</p>
            <h2>Activos disponibles</h2>
          </div>

          {!assetsQuery.isPending && !assetsQuery.isError ? (
            <span className="market-results__count">{total} registros</span>
          ) : null}
        </header>

        {assetsQuery.isPending ? (
          <PageLoadingState message="Cargando activos..." />
        ) : assetsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar los activos"
            message={assetsQuery.error.message}
            onRetry={() => {
              void assetsQuery.refetch()
            }}
          />
        ) : assets.length === 0 ? (
          <PageEmptyState
            title="No se encontraron activos"
            description="No hay activos que coincidan con los filtros seleccionados."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="market-assets">
              {assets.map((asset) => (
                <article className="market-asset" key={asset.id}>
                  <header className="market-asset__header">
                    <div>
                      <strong>{asset.symbol}</strong>
                      <span>{asset.name}</span>
                    </div>

                    <span className={`market-status market-status--${asset.status.toLowerCase()}`}>
                      {formatAssetStatus(asset.status)}
                    </span>
                  </header>

                  <dl className="market-asset__details">
                    <div>
                      <dt>Mercado</dt>
                      <dd>{asset.market.name}</dd>
                    </div>

                    <div>
                      <dt>Tipo</dt>
                      <dd>{asset.asset_type.name}</dd>
                    </div>

                    <div>
                      <dt>Sector</dt>
                      <dd>{asset.sector ?? 'No disponible'}</dd>
                    </div>

                    <div>
                      <dt>Moneda</dt>
                      <dd>{asset.currency}</dd>
                    </div>
                  </dl>
                  <div className="market-asset__actions">
                    <Link
                      className="button button--secondary"
                      to={`/app/market/assets/${asset.id}`}
                    >
                      Ver detalle
                    </Link>
                  </div>
                </article>
              ))}
            </div>

            <footer className="market-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="market-pagination__controls">
                <button
                  className="button button--secondary"
                  type="button"
                  disabled={page === 0}
                  onClick={() => setPage((current) => Math.max(0, current - 1))}
                >
                  Anterior
                </button>

                <span>
                  Página {page + 1} de {totalPages}
                </span>

                <button
                  className="button button--secondary"
                  type="button"
                  disabled={(page + 1) * PAGE_SIZE >= total}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Siguiente
                </button>
              </div>
            </footer>
          </>
        )}
      </section>
    </section>
  )
}
