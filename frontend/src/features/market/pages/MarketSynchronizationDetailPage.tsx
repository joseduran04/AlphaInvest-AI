import { Link, useParams } from 'react-router'

import type { JobExecutionStatus } from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useMarketSynchronization } from '@/features/market/hooks/useMarketSynchronization'

import '@/styles/market-synchronizations.css'

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

function formatResult(result: { [key: string]: unknown } | null): string {
  if (!result) {
    return 'No disponible'
  }

  return JSON.stringify(result, null, 2)
}

export function MarketSynchronizationDetailPage() {
  const { executionId = '' } = useParams<{ executionId: string }>()
  const { hasPermission } = useAuth()

  const canReadJobs = hasPermission('trabajos.leer')
  const synchronizationQuery = useMarketSynchronization(executionId, canReadJobs)

  if (!canReadJobs) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar esta ejecución."
      />
    )
  }

  if (!executionId) {
    return (
      <PageErrorState
        title="Ejecución no válida"
        message="No se recibió un identificador de ejecución válido."
      />
    )
  }

  if (synchronizationQuery.isPending) {
    return <PageLoadingState message="Cargando detalle de sincronización..." />
  }

  if (synchronizationQuery.isError) {
    return (
      <PageErrorState
        title="No fue posible cargar la sincronización"
        message={synchronizationQuery.error.message}
        onRetry={() => {
          void synchronizationQuery.refetch()
        }}
      />
    )
  }

  const execution = synchronizationQuery.data

  return (
    <section className="market-sync-detail">
      <header className="market-sync-detail__header">
        <div>
          <p className="app__eyebrow">Mercado · Sincronizaciones</p>
          <h1>{execution.job.name}</h1>
          <p className="app__description">
            Información registrada para la ejecución {execution.id}.
          </p>
        </div>

        <Link className="button button--secondary" to="/app/market/synchronizations">
          Volver al historial
        </Link>
      </header>

      <section className="market-sync-detail__panel">
        <header className="market-sync-detail__section-header">
          <div>
            <p className="market-sync-results__eyebrow">Ejecución</p>
            <h2>Información general</h2>
          </div>

          <span
            className={`market-sync-status market-sync-status--${execution.status.toLowerCase()}`}
          >
            {formatExecutionStatus(execution.status)}
          </span>
        </header>

        <dl className="market-sync-detail__grid">
          <div>
            <dt>ID</dt>
            <dd>{execution.id}</dd>
          </div>

          <div>
            <dt>Trabajo</dt>
            <dd>{execution.job.name}</dd>
          </div>

          <div>
            <dt>Código</dt>
            <dd>{execution.job.code}</dd>
          </div>

          <div>
            <dt>Tipo</dt>
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
            <dt>Solicitado por</dt>
            <dd>{execution.requested_by ?? 'No disponible'}</dd>
          </div>

          <div>
            <dt>Process ID</dt>
            <dd>{execution.process_id ?? 'No disponible'}</dd>
          </div>

          <div>
            <dt>Solicitado</dt>
            <dd>{formatDateTime(execution.requested_at)}</dd>
          </div>

          <div>
            <dt>Inicio</dt>
            <dd>{formatDateTime(execution.started_at)}</dd>
          </div>

          <div>
            <dt>Fin</dt>
            <dd>{formatDateTime(execution.finished_at)}</dd>
          </div>

          <div>
            <dt>Progreso</dt>
            <dd>{execution.progress}</dd>
          </div>
        </dl>
      </section>

      <section className="market-sync-detail__panel">
        <header className="market-sync-detail__section-header">
          <div>
            <p className="market-sync-results__eyebrow">Procesamiento</p>
            <h2>Registros procesados</h2>
          </div>
        </header>

        <dl className="market-sync-metrics">
          <div>
            <dt>Procesados</dt>
            <dd>{execution.processed_records}</dd>
          </div>

          <div>
            <dt>Exitosos</dt>
            <dd>{execution.successful_records}</dd>
          </div>

          <div>
            <dt>Fallidos</dt>
            <dd>{execution.failed_records}</dd>
          </div>
        </dl>
      </section>

      <section className="market-sync-detail__panel">
        <header className="market-sync-detail__section-header">
          <div>
            <p className="market-sync-results__eyebrow">Resultado</p>
            <h2>Respuesta del proceso</h2>
          </div>
        </header>

        <pre className="market-sync-result">{formatResult(execution.result)}</pre>
      </section>

      {execution.error_message ? (
        <section className="market-sync-detail__panel market-sync-detail__panel--error">
          <header className="market-sync-detail__section-header">
            <div>
              <p className="market-sync-results__eyebrow">Error</p>
              <h2>Mensaje registrado</h2>
            </div>
          </header>

          <p className="market-sync-error-message">{execution.error_message}</p>
        </section>
      ) : null}
    </section>
  )
}
