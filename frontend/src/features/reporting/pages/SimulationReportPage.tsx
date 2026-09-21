import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type {
  SimulationExecutionStatus,
  SimulationReportExportQuery,
  SimulationReportListQuery,
  SimulationType,
} from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useSimulationReports } from '@/features/reporting/hooks/useSimulationReports'
import { useExportSimulationReports } from '@/features/reporting/hooks/useExportSimulationReports'
import { formatCurrency } from '@/lib/formatters'

import '@/styles/reporting.css'

const PAGE_SIZE = 20

interface SimulationReportFilters {
  status: SimulationExecutionStatus | ''
  type: SimulationType | ''
  dateFrom: string
  dateTo: string
}

const initialFilters: SimulationReportFilters = {
  status: '',
  type: '',
  dateFrom: '',
  dateTo: '',
}

function formatSimulationType(type: string | null): string {
  switch (type) {
    case 'HISTORICA':
      return 'Histórica'
    case 'MONTE_CARLO':
      return 'Monte Carlo'
    case 'PROYECCION':
      return 'Proyección'
    case 'ESCENARIO':
      return 'Escenario'
    default:
      return type ?? 'No disponible'
  }
}

function formatExecutionStatus(status: string | null): string {
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
    default:
      return status ?? 'No disponible'
  }
}

function formatPercentage(value: string | number | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return `${value}%`
  }

  return `${parsedValue.toFixed(2)}%`
}

function formatDecimal(value: string | number | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return String(value)
  }

  return parsedValue.toFixed(2)
}

function formatReportCurrency(
  value: string | number | null | undefined,
  currency: string | null,
): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  if (!currency) {
    return String(value)
  }

  return formatCurrency(value, currency)
}

function formatDuration(value: string | number | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const seconds = Number(value)

  if (!Number.isFinite(seconds)) {
    return String(value)
  }

  if (seconds < 60) {
    return `${seconds.toFixed(2)} s`
  }

  return `${(seconds / 60).toFixed(2)} min`
}

export function SimulationReportPage() {
  const { hasPermission } = useAuth()

  const canReadReports = hasPermission('reportes.leer')
  const canExportReports = hasPermission('reportes.exportar')

  const [draftFilters, setDraftFilters] = useState<SimulationReportFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<SimulationReportFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const params: SimulationReportListQuery = {
    status: appliedFilters.status || undefined,
    type: appliedFilters.type || undefined,
    date_from: appliedFilters.dateFrom || undefined,
    date_to: appliedFilters.dateTo || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const reportsQuery = useSimulationReports(params, canReadReports)
  const exportReports = useExportSimulationReports()

  const exportParams: SimulationReportExportQuery = {
    status: appliedFilters.status || undefined,
    type: appliedFilters.type || undefined,
    date_from: appliedFilters.dateFrom || undefined,
    date_to: appliedFilters.dateTo || undefined,
    limit: 5000,
    offset: 0,
  }

  if (!canReadReports) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar reportes."
      />
    )
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setAppliedFilters(draftFilters)
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
    <section className="reporting-page">
      <header className="reporting-page__header">
        <div>
          <p className="app__eyebrow">Reportes</p>
          <h1>Reporte de simulaciones</h1>
          <p className="app__description">
            Consulta ejecuciones, resultados y métricas financieras obtenidas en tus simulaciones.
          </p>
        </div>

        <Link className="button button--secondary" to="/app/reports">
          Centro de reportes
        </Link>
      </header>

      <form className="reporting-filters" onSubmit={handleSubmit}>
        <div className="reporting-section__header">
          <div>
            <h2>Filtros</h2>
            <p>Refina el reporte por estado, tipo y fecha de solicitud.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="reporting-filters__grid">
          <label className="reporting-field">
            <span>Estado</span>
            <select
              value={draftFilters.status}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  status: event.target.value as SimulationExecutionStatus | '',
                }))
              }
            >
              <option value="">Todos</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="EJECUTANDO">Ejecutando</option>
              <option value="COMPLETADA">Completada</option>
              <option value="FALLIDA">Fallida</option>
              <option value="CANCELADA">Cancelada</option>
            </select>
          </label>

          <label className="reporting-field">
            <span>Tipo</span>
            <select
              value={draftFilters.type}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  type: event.target.value as SimulationType | '',
                }))
              }
            >
              <option value="">Todos</option>
              <option value="HISTORICA">Histórica</option>
              <option value="MONTE_CARLO">Monte Carlo</option>
              <option value="PROYECCION">Proyección</option>
              <option value="ESCENARIO">Escenario</option>
            </select>
          </label>

          <label className="reporting-field">
            <span>Fecha desde</span>
            <input
              type="date"
              value={draftFilters.dateFrom}
              max={draftFilters.dateTo || undefined}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  dateFrom: event.target.value,
                }))
              }
            />
          </label>

          <label className="reporting-field">
            <span>Fecha hasta</span>
            <input
              type="date"
              value={draftFilters.dateTo}
              min={draftFilters.dateFrom || undefined}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  dateTo: event.target.value,
                }))
              }
            />
          </label>
        </div>

        <div className="reporting-filters__actions">
          <button className="button button--primary" type="submit">
            Aplicar filtros
          </button>
        </div>
      </form>

      <section className="reporting-results">
        <header className="reporting-section__header">
          <div>
            <p className="reporting-overview__eyebrow">Resultados</p>
            <h2>Simulaciones consolidadas</h2>
          </div>

          <div className="reporting-results__actions">
            {!reportsQuery.isPending && !reportsQuery.isError ? (
              <span className="reporting-results__count">{total} registros</span>
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
          <p className="reporting-export-error" role="alert">
            No fue posible exportar el reporte: {exportReports.error.message}
          </p>
        ) : null}

        {reportsQuery.isPending ? (
          <PageLoadingState message="Cargando reporte de simulaciones..." />
        ) : reportsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar el reporte de simulaciones"
            message={reportsQuery.error.message}
            onRetry={() => {
              void reportsQuery.refetch()
            }}
          />
        ) : reports.length === 0 ? (
          <PageEmptyState
            title="No se encontraron simulaciones"
            description="No existen ejecuciones que coincidan con los filtros seleccionados."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="reporting-table-wrapper">
              <table className="reporting-table reporting-table--simulation">
                <thead>
                  <tr>
                    <th>Simulación</th>
                    <th>Estado</th>
                    <th>Período</th>
                    <th>Capital configurado</th>
                    <th>Capital final</th>
                    <th>P&amp;L</th>
                    <th>Rendimiento</th>
                    <th>Volatilidad</th>
                    <th>Sharpe</th>
                    <th>Drawdown</th>
                    <th>VaR</th>
                    <th>Prob. ganancia</th>
                    <th>Modelo</th>
                    <th>Duración</th>
                  </tr>
                </thead>

                <tbody>
                  {reports.map((report, index) => (
                    <tr
                      key={
                        report.execution_id ?? `${report.configuration_id ?? 'simulation'}-${index}`
                      }
                    >
                      <td>
                        <strong>{report.configuration_name ?? 'Sin nombre'}</strong>
                        <span>{formatSimulationType(report.simulation_type)}</span>
                      </td>

                      <td>
                        <strong>{formatExecutionStatus(report.status)}</strong>
                        <span>{formatPercentage(report.progress_percentage)} progreso</span>
                      </td>

                      <td>
                        <strong>{report.period_start ?? 'No disponible'}</strong>
                        <span>{report.period_end ?? 'No disponible'}</span>
                      </td>

                      <td>
                        {formatReportCurrency(report.configured_capital, report.base_currency)}
                      </td>

                      <td>
                        {report.result_available
                          ? formatReportCurrency(report.final_capital, report.base_currency)
                          : 'Sin resultado'}
                      </td>

                      <td>
                        {report.result_available
                          ? formatReportCurrency(report.profit_loss, report.base_currency)
                          : 'Sin resultado'}
                      </td>

                      <td>
                        {report.result_available
                          ? formatPercentage(report.total_return_percentage)
                          : 'Sin resultado'}
                      </td>

                      <td>
                        {report.result_available
                          ? formatPercentage(report.annualized_volatility)
                          : 'Sin resultado'}
                      </td>

                      <td>
                        {report.result_available
                          ? formatDecimal(report.sharpe_ratio)
                          : 'Sin resultado'}
                      </td>

                      <td>
                        {report.result_available
                          ? formatPercentage(report.max_drawdown_percentage)
                          : 'Sin resultado'}
                      </td>

                      <td>
                        {report.result_available
                          ? formatReportCurrency(report.value_at_risk, report.base_currency)
                          : 'Sin resultado'}
                      </td>

                      <td>
                        {report.result_available
                          ? formatPercentage(report.gain_probability)
                          : 'Sin resultado'}
                      </td>

                      <td>
                        <strong>{report.model_name ?? 'No disponible'}</strong>
                        <span>
                          {report.model_version
                            ? `v${report.model_version}`
                            : 'Versión no disponible'}
                        </span>
                      </td>

                      <td>{formatDuration(report.duration_seconds)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <footer className="reporting-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="reporting-pagination__controls">
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
