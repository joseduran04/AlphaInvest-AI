import { type FormEvent, useRef, useState } from 'react'

import type { AssetNewsListQuery } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useAssets } from '@/features/market/hooks/useAssets'
import { NewsCard } from '@/features/news/components/NewsCard'
import { useAssetNews } from '@/features/news/hooks/useAssetNews'
import { useSyncAssetNews } from '@/features/news/hooks/useSyncAssetNews'

import '@/styles/news.css'

const PAGE_SIZE = 20

interface NewsFilters {
  assetId: string
  startDate: string
  endDate: string
}

const initialFilters: NewsFilters = {
  assetId: '',
  startDate: '',
  endDate: '',
}

function toStartDateTime(value: string): string | undefined {
  return value ? `${value}T00:00:00` : undefined
}

function toEndDateTime(value: string): string | undefined {
  return value ? `${value}T23:59:59` : undefined
}

function formatFilterDate(value: string): string {
  if (!value) {
    return 'Sin límite'
  }

  const [year, month, day] = value.split('-')

  return `${day}/${month}/${year}`
}

export function NewsPage() {
  const { hasPermission } = useAuth()

  const canReadNews = hasPermission('noticias.leer')
  const canSyncNews = hasPermission('noticias.cargar')
  const canReadAssets = hasPermission('activos.leer')

  const [draftFilters, setDraftFilters] = useState<NewsFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<NewsFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const resultsRef = useRef<HTMLElement>(null)

  const assetsQuery = useAssets(
    {
      status: 'ACTIVO',
      limit: 100,
      offset: 0,
    },
    canReadNews && canReadAssets,
  )

  const params: AssetNewsListQuery = {
    start_at: toStartDateTime(appliedFilters.startDate),
    end_at: toEndDateTime(appliedFilters.endDate),
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const newsQuery = useAssetNews(
    appliedFilters.assetId || null,
    params,
    canReadNews && canReadAssets && Boolean(appliedFilters.assetId),
  )

  const syncNewsMutation = useSyncAssetNews(appliedFilters.assetId)

  if (!canReadNews) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar noticias financieras."
      />
    )
  }

  if (!canReadAssets) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar los activos asociados a las noticias."
      />
    )
  }

  const hasInvalidDateRange =
    Boolean(draftFilters.startDate) &&
    Boolean(draftFilters.endDate) &&
    draftFilters.startDate > draftFilters.endDate

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!draftFilters.assetId || hasInvalidDateRange) {
      return
    }

    syncNewsMutation.reset()
    setAppliedFilters(draftFilters)
    setPage(0)
  }

  function handleReset() {
    syncNewsMutation.reset()
    setDraftFilters(initialFilters)
    setAppliedFilters(initialFilters)
    setPage(0)
  }

  function handlePageChange(nextPage: number) {
    setPage(nextPage)

    window.requestAnimationFrame(() => {
      resultsRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    })
  }

  function handleSynchronization() {
    if (!appliedFilters.assetId || !canSyncNews || syncNewsMutation.isPending) {
      return
    }

    syncNewsMutation.mutate({
      start_at: toStartDateTime(appliedFilters.startDate),
      end_at: toEndDateTime(appliedFilters.endDate),
      limit: PAGE_SIZE,
    })
  }

  const assets = assetsQuery.data?.items ?? []
  const news = newsQuery.data?.items ?? []
  const total = newsQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const firstResult = total === 0 ? 0 : page * PAGE_SIZE + 1
  const lastResult = Math.min((page + 1) * PAGE_SIZE, total)

  const hasAppliedAsset = Boolean(appliedFilters.assetId)
  const selectedAsset = assets.find((asset) => asset.id === appliedFilters.assetId)

  return (
    <section className="news-page">
      <header className="news-page__header">
        <div>
          <p className="app__eyebrow">Noticias</p>
          <h1>Noticias financieras</h1>
          <p className="app__description">
            Consulta las noticias financieras registradas para los activos disponibles en
            AlphaInvest AI.
          </p>
          <p className="metric-hint">
            El tono (alcista, neutral o bajista) y la relevancia los calcula el proveedor de
            noticias. Un tono alcista describe cómo está escrita la noticia; no garantiza que el
            precio suba.
          </p>
        </div>
      </header>

      <form className="news-filters" onSubmit={handleSubmit}>
        <div className="news-filters__header">
          <div>
            <h2>Consulta</h2>
            <p>
              Selecciona un activo y, si lo deseas, limita las noticias por fecha de publicación.
            </p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="news-filters__grid">
          <label className="news-field news-field--asset">
            <span>Activo</span>

            <select
              value={draftFilters.assetId}
              required
              disabled={assetsQuery.isPending || assetsQuery.isError}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  assetId: event.target.value,
                }))
              }
            >
              <option value="">Selecciona un activo</option>

              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.symbol} — {asset.name}
                </option>
              ))}
            </select>
          </label>

          <label className="news-field">
            <span>Desde</span>
            <input
              type="date"
              value={draftFilters.startDate}
              max={draftFilters.endDate || undefined}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  startDate: event.target.value,
                }))
              }
            />
          </label>

          <label className="news-field">
            <span>Hasta</span>
            <input
              type="date"
              value={draftFilters.endDate}
              min={draftFilters.startDate || undefined}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  endDate: event.target.value,
                }))
              }
            />
          </label>
        </div>

        {hasInvalidDateRange ? (
          <p className="news-filters__error" role="alert">
            La fecha inicial no puede ser posterior a la fecha final.
          </p>
        ) : null}

        <div className="news-filters__actions">
          <button
            className="button button--primary"
            type="submit"
            disabled={assetsQuery.isPending || !draftFilters.assetId || hasInvalidDateRange}
          >
            Consultar noticias
          </button>
        </div>
      </form>

      <section className="news-results" ref={resultsRef}>
        <header className="news-results__header">
          <div>
            <p className="news-results__eyebrow">Resultados</p>
            <h2>Noticias disponibles</h2>
          </div>

          {hasAppliedAsset && !newsQuery.isPending && !newsQuery.isError ? (
            <span className="news-results__count">{total} noticias</span>
          ) : null}
        </header>

        {hasAppliedAsset ? (
          <div className="news-applied-filters">
            <div>
              <span>Activo</span>
              <strong>
                {selectedAsset
                  ? `${selectedAsset.symbol} — ${selectedAsset.name}`
                  : 'Activo seleccionado'}
              </strong>
            </div>

            <div>
              <span>Desde</span>
              <strong>{formatFilterDate(appliedFilters.startDate)}</strong>
            </div>

            <div>
              <span>Hasta</span>
              <strong>{formatFilterDate(appliedFilters.endDate)}</strong>
            </div>
          </div>
        ) : null}

        {hasAppliedAsset && canSyncNews ? (
          <section className="news-sync">
            <div>
              <h3>Sincronización de noticias</h3>
              <p>
                Consulta la fuente financiera y actualiza las noticias almacenadas para el activo y
                periodo seleccionados.
              </p>
            </div>

            <button
              className="button button--secondary"
              type="button"
              disabled={syncNewsMutation.isPending}
              onClick={handleSynchronization}
            >
              {syncNewsMutation.isPending ? 'Sincronizando...' : 'Sincronizar noticias'}
            </button>
          </section>
        ) : null}

        {hasAppliedAsset && canSyncNews && syncNewsMutation.isError ? (
          <div className="news-sync__feedback news-sync__feedback--error" role="alert">
            {syncNewsMutation.error.message}
          </div>
        ) : null}

        {hasAppliedAsset && canSyncNews && syncNewsMutation.isSuccess ? (
          <div className="news-sync__feedback news-sync__feedback--success" role="status">
            <strong>Sincronización completada.</strong>
            <span>
              Recibidas: {syncNewsMutation.data.received} · Creadas: {syncNewsMutation.data.created}{' '}
              · Reutilizadas: {syncNewsMutation.data.reused} · Fallidas:{' '}
              {syncNewsMutation.data.failed}
            </span>
          </div>
        ) : null}

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
            title="No hay activos disponibles"
            description="No existen activos disponibles para consultar noticias."
          />
        ) : !hasAppliedAsset ? (
          <PageEmptyState
            title="Selecciona un activo"
            description="Selecciona un activo para consultar las noticias financieras asociadas."
          />
        ) : newsQuery.isPending ? (
          <PageLoadingState message="Cargando noticias..." />
        ) : newsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar las noticias"
            message={newsQuery.error.message}
            onRetry={() => {
              void newsQuery.refetch()
            }}
          />
        ) : news.length === 0 ? (
          <PageEmptyState
            title="No se encontraron noticias"
            description="No hay noticias registradas para el activo y el rango de fechas seleccionados."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="news-feed">
              {news.map((item) => (
                <NewsCard key={item.reference_id} news={item} />
              ))}
            </div>

            <footer className="news-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="news-pagination__controls">
                <button
                  className="button button--secondary"
                  type="button"
                  disabled={page === 0 || newsQuery.isFetching}
                  onClick={() => handlePageChange(Math.max(0, page - 1))}
                >
                  Anterior
                </button>

                <span>
                  Página {page + 1} de {totalPages}
                </span>

                <button
                  className="button button--secondary"
                  type="button"
                  disabled={(page + 1) * PAGE_SIZE >= total || newsQuery.isFetching}
                  onClick={() => handlePageChange(page + 1)}
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
