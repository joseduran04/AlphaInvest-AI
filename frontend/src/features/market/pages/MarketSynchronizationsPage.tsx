import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type { JobExecutionStatus, MarketSynchronizationListQuery } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useMarketSynchronizations } from '@/features/market/hooks/useMarketSynchronizations'

import '@/styles/market-synchronizations.css'

const PAGE_SIZE = 20

function formatExecutionStatus(status: JobExecutionStatus): string {
  switch (status) {
    case 'PENDIENTE':
      return 'Pendiente'
    case 'EJECUTANDO':
      return 'Ejecutando'
    case 'COMPLETADA':
      return 'Completada'
    case 'FALLIDA':
      return 'Fallida'
    case 'CANCELADA':
      return 'Cancelada'
    case 'OMITIDA':
      return 'Omitida'
  }
}

function formatDateTime(value: string | null): string {
  if (!value) {
    return 'No disponible'
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function MarketSynchronizationsPage() {
  const { hasPermission } = useAuth()
  const canReadJobs = hasPermission('trabajos.leer')

  const [draftStatus, setDraftStatus] = useState<JobExecutionStatus | ''>('')
  const [appliedStatus, setAppliedStatus] = useState<JobExecutionStatus | ''>('')
  const [page, setPage] = useState(0)

  const params: MarketSynchronizationListQuery = {
    status: appliedStatus || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const synchronizationsQuery = useMarketSynchronizations(params, canReadJobs)

  if (!canReadJobs) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar ejecuciones de sincronización."
      />
    )
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setAppliedStatus(draftStatus)
    setPage(0)
  }

  function handleReset() {
    setDraftStatus('')
    setAppliedStatus('')
    setPage(0)
  }

  const executions = synchronizationsQuery.data?.items ?? []
  const total = synchronizationsQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const firstResult = total === 0 ? 0 : page * PAGE_SIZE + 1
  const lastResult = Math.min((page + 1) * PAGE_SIZE, total)

  return (
    <section className="market-sync-page">
      <header className="market-sync-page__header">
        <div>
          <p className="app__eyebrow">Mercado</p>
          <h1>Sincronizaciones</h1>
          <p className="app__description">
            Consulta las ejecuciones registradas para los procesos de sincronización de mercado.
          </p>
        </div>
      </header>

      <form className="market-sync-filters" onSubmit={handleSubmit}>
        <div className="market-sync-filters__header">
          <div>
            <h2>Filtros</h2>
            <p>Filtra las ejecuciones utilizando el estado registrado por el backend.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="market-sync-filters__grid">
          <label className="market-sync-field">
            <span>Estado</span>

            <select
              value={draftStatus}
              onChange={(event) => setDraftStatus(event.target.value as JobExecutionStatus | '')}
            >
              <option value="">Todos</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="EJECUTANDO">Ejecutando</option>
              <option value="COMPLETADA">Completada</option>
              <option value="FALLIDA">Fallida</option>
              <option value="CANCELADA">Cancelada</option>
              <option value="OMITIDA">Omitida</option>
            </select>
          </label>
        </div>

        <div className="market-sync-filters__actions">
          <button className="button button--primary" type="submit">
            Aplicar filtros
          </button>
        </div>
      </form>

      <section className="market-sync-results">
        <header className="market-sync-results__header">
          <div>
            <p className="market-sync-results__eyebrow">Resultados</p>
            <h2>Historial de ejecuciones</h2>
          </div>

          {!synchronizationsQuery.isPending && !synchronizationsQuery.isError ? (
            <span className="market-sync-results__count">{total} registros</span>
          ) : null}
        </header>

        {synchronizationsQuery.isPending ? (
          <PageLoadingState message="Cargando sincronizaciones..." />
        ) : synchronizationsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar las sincronizaciones"
            message={synchronizationsQuery.error.message}
            onRetry={() => {
              void synchronizationsQuery.refetch()
            }}
          />
        ) : executions.length === 0 ? (
          <PageEmptyState
            title="No se encontraron sincronizaciones"
            description="No hay ejecuciones que coincidan con el estado seleccionado."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="market-sync-list">
              {executions.map((execution) => (
                <article className="market-sync-card" key={execution.id}>
                  <header className="market-sync-card__header">
                    <div>
                      <strong>{execution.job.name}</strong>
                      <span>{execution.job.code}</span>
                    </div>

                    <span
                      className={`market-sync-status market-sync-status--${execution.status.toLowerCase()}`}
                    >
                      {formatExecutionStatus(execution.status)}
                    </span>
                  </header>

                  <dl className="market-sync-card__details">
                    <div>
                      <dt>Tipo de trabajo</dt>
                      <dd>{execution.job.type}</dd>
                    </div>

                    <div>
                      <dt>Disparador</dt>
                      <dd>{execution.trigger}</dd>
                    </div>

                    <div>
                      <dt>Intento</dt>
                      <dd>{execution.attempt}</dd>
                    </div>

                    <div>
                      <dt>Solicitado</dt>
                      <dd>{formatDateTime(execution.requested_at)}</dd>
                    </div>

                    <div>
                      <dt>Progreso</dt>
                      <dd>{execution.progress}</dd>
                    </div>

                    <div>
                      <dt>Procesados</dt>
                      <dd>{execution.processed_records}</dd>
                    </div>
                  </dl>

                  <div className="market-sync-card__actions">
                    <Link
                      className="button button--secondary"
                      to={`/app/market/synchronizations/${execution.id}`}
                    >
                      Ver detalle
                    </Link>
                  </div>
                </article>
              ))}
            </div>

            <footer className="market-sync-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="market-sync-pagination__controls">
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
