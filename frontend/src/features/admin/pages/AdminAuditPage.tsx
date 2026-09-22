import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type { AuditReportExportQuery, AuditReportListQuery } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useAuditReports } from '@/features/reporting/hooks/useAuditReports'
import { useExportAuditReports } from '@/features/reporting/hooks/useExportAuditReports'

import '@/styles/admin.css'

const PAGE_SIZE = 20

interface AdminAuditFilters {
  entitySchema: string
  entityName: string
  action: string
  origin: string
  dateFrom: string
  dateTo: string
}

const initialFilters: AdminAuditFilters = {
  entitySchema: '',
  entityName: '',
  action: '',
  origin: '',
  dateFrom: '',
  dateTo: '',
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

export function AdminAuditPage() {
  const { hasPermission } = useAuth()

  const canManageReports = hasPermission('reportes.administrar')
  const canExportReports = hasPermission('reportes.exportar')

  const [draftFilters, setDraftFilters] = useState<AdminAuditFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<AdminAuditFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const params: AuditReportListQuery = {
    entity_schema: appliedFilters.entitySchema.trim() || undefined,
    entity_name: appliedFilters.entityName.trim() || undefined,
    action: appliedFilters.action.trim() || undefined,
    origin: appliedFilters.origin.trim() || undefined,
    date_from: appliedFilters.dateFrom || undefined,
    date_to: appliedFilters.dateTo || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const reportsQuery = useAuditReports(params, canManageReports)
  const exportReports = useExportAuditReports()

  const exportParams: AuditReportExportQuery = {
    entity_schema: appliedFilters.entitySchema.trim() || undefined,
    entity_name: appliedFilters.entityName.trim() || undefined,
    action: appliedFilters.action.trim() || undefined,
    origin: appliedFilters.origin.trim() || undefined,
    date_from: appliedFilters.dateFrom || undefined,
    date_to: appliedFilters.dateTo || undefined,
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
      entitySchema: draftFilters.entitySchema.trim(),
      entityName: draftFilters.entityName.trim(),
      action: draftFilters.action.trim(),
      origin: draftFilters.origin.trim(),
      dateFrom: draftFilters.dateFrom,
      dateTo: draftFilters.dateTo,
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
          <h1>Auditoría del sistema</h1>
          <p className="app__description">
            Consulta la actividad consolidada registrada por las entidades auditadas de AlphaInvest
            AI.
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
            <p>Refina los eventos de auditoría utilizando los criterios disponibles.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="admin-filters__grid">
          <label className="admin-field">
            <span>Esquema</span>
            <input
              type="text"
              value={draftFilters.entitySchema}
              placeholder="Ej. operation"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  entitySchema: event.target.value,
                }))
              }
            />
          </label>

          <label className="admin-field">
            <span>Entidad</span>
            <input
              type="text"
              value={draftFilters.entityName}
              placeholder="Ej. trabajos_programados"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  entityName: event.target.value,
                }))
              }
            />
          </label>

          <label className="admin-field">
            <span>Acción</span>
            <input
              type="text"
              value={draftFilters.action}
              placeholder="Ej. UPDATE"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  action: event.target.value,
                }))
              }
            />
          </label>

          <label className="admin-field">
            <span>Origen</span>
            <input
              type="text"
              value={draftFilters.origin}
              placeholder="Ej. BASE_DATOS"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  origin: event.target.value,
                }))
              }
            />
          </label>

          <label className="admin-field">
            <span>Desde</span>
            <input
              type="date"
              value={draftFilters.dateFrom}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  dateFrom: event.target.value,
                }))
              }
            />
          </label>

          <label className="admin-field">
            <span>Hasta</span>
            <input
              type="date"
              value={draftFilters.dateTo}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  dateTo: event.target.value,
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
            <h2>Actividad auditada</h2>
          </div>

          <div className="admin-results__actions">
            {!reportsQuery.isPending && !reportsQuery.isError ? (
              <span className="admin-results__count">{total} registros</span>
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
          <PageLoadingState message="Cargando auditoría del sistema..." />
        ) : reportsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar la auditoría"
            message={reportsQuery.error.message}
            onRetry={() => {
              void reportsQuery.refetch()
            }}
          />
        ) : reports.length === 0 ? (
          <PageEmptyState
            title="No se encontraron eventos"
            description="No existen registros de auditoría que coincidan con los filtros seleccionados."
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
                    <th>Fecha</th>
                    <th>Entidad</th>
                    <th>Acción</th>
                    <th>Origen</th>
                    <th>Eventos</th>
                    <th>Usuarios involucrados</th>
                    <th>Sin usuario</th>
                    <th>Primer evento</th>
                    <th>Último evento</th>
                  </tr>
                </thead>

                <tbody>
                  {reports.map((report) => (
                    <tr
                      key={`${report.date}-${report.entity_schema}-${report.entity_name}-${report.action}-${report.origin}`}
                    >
                      <td>{report.date}</td>
                      <td>
                        <strong>{report.entity_name}</strong>
                        <span>{report.entity_schema}</span>
                      </td>
                      <td>{report.action}</td>
                      <td>{report.origin}</td>
                      <td>{report.total_events}</td>
                      <td>{report.involved_users}</td>
                      <td>{report.events_without_user}</td>
                      <td>{formatDateTime(report.first_event_at)}</td>
                      <td>{formatDateTime(report.last_event_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

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
