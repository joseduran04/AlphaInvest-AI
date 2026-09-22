import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type { OperationJobReportExportQuery, OperationJobReportListQuery } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useExportOperationJobReports } from '@/features/reporting/hooks/useExportOperationJobReports'
import { useOperationJobReports } from '@/features/reporting/hooks/useOperationJobReports'

import '@/styles/admin.css'

const PAGE_SIZE = 20

type BooleanFilter = '' | 'true' | 'false'

interface AdminJobFilters {
  active: BooleanFilter
  type: string
  lastStatus: string
}

const initialFilters: AdminJobFilters = {
  active: '',
  type: '',
  lastStatus: '',
}

function toOptionalBoolean(value: BooleanFilter): boolean | undefined {
  if (value === '') {
    return undefined
  }

  return value === 'true'
}

function formatBoolean(value: boolean | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  return value ? 'Sí' : 'No'
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString('es-MX')
}

function formatProgress(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const progress = Number(value)

  if (Number.isNaN(progress)) {
    return value
  }

  return `${progress.toFixed(2)} %`
}

function formatSchedule(
  type: string | null | undefined,
  cronExpression: string | null | undefined,
  intervalSeconds: number | null | undefined,
): string {
  if (type === 'CRON' && cronExpression) {
    return `CRON: ${cronExpression}`
  }

  if (type === 'INTERVALO' && intervalSeconds !== null && intervalSeconds !== undefined) {
    return `Cada ${intervalSeconds} s`
  }

  if (type === 'MANUAL') {
    return 'Ejecución manual'
  }

  return 'No disponible'
}

export function AdminJobsPage() {
  const { hasPermission } = useAuth()

  const canManageReports = hasPermission('reportes.administrar')
  const canExportReports = hasPermission('reportes.exportar')

  const [draftFilters, setDraftFilters] = useState<AdminJobFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<AdminJobFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const params: OperationJobReportListQuery = {
    active: toOptionalBoolean(appliedFilters.active),
    type: appliedFilters.type.trim() || undefined,
    last_status: appliedFilters.lastStatus.trim() || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const reportsQuery = useOperationJobReports(params, canManageReports)
  const exportReports = useExportOperationJobReports()

  const exportParams: OperationJobReportExportQuery = {
    active: toOptionalBoolean(appliedFilters.active),
    type: appliedFilters.type.trim() || undefined,
    last_status: appliedFilters.lastStatus.trim() || undefined,
    limit: 5000,
    offset: 0,
  }

  if (!canManageReports) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar reportes administrativos."
      />
    )
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setAppliedFilters({
      active: draftFilters.active,
      type: draftFilters.type.trim(),
      lastStatus: draftFilters.lastStatus.trim(),
    })
    setPage(0)
  }

  function handleReset() {
    setDraftFilters(initialFilters)
    setAppliedFilters(initialFilters)
    setPage(0)
  }

  const reports = reportsQuery.data?.items ?? []
  const total = reportsQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const firstResult = total === 0 ? 0 : page * PAGE_SIZE + 1
  const lastResult = Math.min((page + 1) * PAGE_SIZE, total)

  return (
    <section className="admin-page">
      <header className="admin-page__header">
        <div>
          <p className="app__eyebrow">Administración</p>
          <h1>Trabajos programados</h1>
          <p className="app__description">
            Supervisa la configuración y el estado operativo de los trabajos de AlphaInvest AI.
          </p>
        </div>

        <Link className="button button--secondary" to="/app/admin">
          Centro de administración
        </Link>
      </header>

      <form className="admin-filters" onSubmit={handleSubmit}>
        <div className="admin-section__header">
          <div>
            <h2>Filtros</h2>
            <p>Consulta trabajos por estado, tipo y resultado de su última ejecución.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="admin-filters__grid">
          <label className="admin-field">
            <span>Activo</span>
            <select
              value={draftFilters.active}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  active: event.target.value as BooleanFilter,
                }))
              }
            >
              <option value="">Todos</option>
              <option value="true">Sí</option>
              <option value="false">No</option>
            </select>
          </label>

          <label className="admin-field">
            <span>Tipo</span>
            <input
              type="text"
              value={draftFilters.type}
              placeholder="Ej. INTERVALO"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  type: event.target.value,
                }))
              }
            />
          </label>

          <label className="admin-field">
            <span>Último estado</span>
            <input
              type="text"
              value={draftFilters.lastStatus}
              placeholder="Ej. COMPLETADA"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  lastStatus: event.target.value,
                }))
              }
            />
          </label>
        </div>

        <div className="admin-filters__actions">
          <button className="button button--primary" type="submit">
            Aplicar filtros
          </button>
        </div>
      </form>

      <section className="admin-results">
        <header className="admin-section__header">
          <div>
            <p className="admin-overview__eyebrow">Resultados</p>
            <h2>Estado operativo</h2>
          </div>

          <div className="admin-results__actions">
            {!reportsQuery.isPending && !reportsQuery.isError ? (
              <span className="admin-results__count">{total} trabajos</span>
            ) : null}

            {canExportReports ? (
              <button
                className="button button--secondary"
                type="button"
                disabled={exportReports.isPending}
                onClick={() => exportReports.mutate(exportParams)}
              >
                {exportReports.isPending ? 'Exportando...' : 'Exportar CSV'}
              </button>
            ) : null}
          </div>
        </header>

        {exportReports.isError ? (
          <p className="admin-export-error" role="alert">
            No fue posible exportar el reporte: {exportReports.error.message}
          </p>
        ) : null}

        {reportsQuery.isPending ? (
          <PageLoadingState message="Cargando trabajos programados..." />
        ) : reportsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar los trabajos"
            message={reportsQuery.error.message}
            onRetry={() => {
              void reportsQuery.refetch()
            }}
          />
        ) : reports.length === 0 ? (
          <PageEmptyState
            title="No se encontraron trabajos"
            description="No existen trabajos que coincidan con los filtros seleccionados."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="admin-table-wrapper">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Trabajo</th>
                    <th>Tipo</th>
                    <th>Activo</th>
                    <th>Programación</th>
                    <th>Último estado</th>
                    <th>Progreso</th>
                    <th>Registros</th>
                    <th>Próxima ejecución</th>
                    <th>Última finalización</th>
                  </tr>
                </thead>

                <tbody>
                  {reports.map((report) => (
                    <tr key={report.job_id ?? report.code ?? undefined}>
                      <td>
                        <strong>{report.name ?? 'Sin nombre'}</strong>
                        <span>{report.code ?? 'Sin código'}</span>
                      </td>
                      <td>{report.type ?? 'No disponible'}</td>
                      <td>{formatBoolean(report.active)}</td>
                      <td>
                        <strong>
                          {formatSchedule(
                            report.type,
                            report.cron_expression,
                            report.interval_seconds,
                          )}
                        </strong>
                        <span>{report.timezone ?? 'Sin zona horaria'}</span>
                      </td>
                      <td>{report.last_execution_status ?? 'Sin ejecución'}</td>
                      <td>{formatProgress(report.last_execution_progress)}</td>
                      <td>
                        <strong>{report.processed_records ?? 0} procesados</strong>
                        <span>
                          {report.successful_records ?? 0} exitosos / {report.failed_records ?? 0}{' '}
                          fallidos
                        </span>
                      </td>
                      <td>{formatDateTime(report.next_execution_at)}</td>
                      <td>{formatDateTime(report.last_execution_finished_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {reports.some((report) => report.last_execution_error) ? (
              <section className="admin-job-errors">
                <div>
                  <p className="admin-overview__eyebrow">Incidencias</p>
                  <h3>Errores de última ejecución</h3>
                </div>

                <div className="admin-job-errors__list">
                  {reports
                    .filter((report) => report.last_execution_error)
                    .map((report) => (
                      <article
                        className="admin-job-error"
                        key={`error-${report.job_id ?? report.code ?? 'job'}`}
                      >
                        <strong>{report.name ?? report.code ?? 'Trabajo sin identificar'}</strong>
                        <pre>{report.last_execution_error}</pre>
                      </article>
                    ))}
                </div>
              </section>
            ) : null}

            <footer className="admin-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="admin-pagination__controls">
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
                  disabled={page + 1 >= totalPages}
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
