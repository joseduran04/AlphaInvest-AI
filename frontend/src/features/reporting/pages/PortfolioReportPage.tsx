import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type {
  PortfolioReportExportQuery,
  PortfolioReportListQuery,
  PortfolioStatus,
  PortfolioType,
} from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { usePortfolioReports } from '@/features/reporting/hooks/usePortfolioReports'
import { useExportPortfolioReports } from '@/features/reporting/hooks/useExportPortfolioReports'
import { formatCurrency } from '@/lib/formatters'

import '@/styles/reporting.css'
import { getFinancialToneClass } from '@/lib/financialTone'

const PAGE_SIZE = 20

interface PortfolioReportFilters {
  status: PortfolioStatus | ''
  type: PortfolioType | ''
}

const initialFilters: PortfolioReportFilters = {
  status: '',
  type: '',
}

function formatPortfolioStatus(status: string | null): string {
  switch (status) {
    case 'ACTIVO':
      return 'Activo'
    case 'CERRADO':
      return 'Cerrado'
    case 'ARCHIVADO':
      return 'Archivado'
    default:
      return status ?? 'No disponible'
  }
}

function formatPortfolioType(type: string | null): string {
  switch (type) {
    case 'VIRTUAL':
      return 'Virtual'
    case 'SIMULADO':
      return 'Simulado'
    default:
      return type ?? 'No disponible'
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

export function PortfolioReportPage() {
  const { hasPermission } = useAuth()

  const canReadReports = hasPermission('reportes.leer')
  const canExportReports = hasPermission('reportes.exportar')

  const [draftFilters, setDraftFilters] = useState<PortfolioReportFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<PortfolioReportFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const params: PortfolioReportListQuery = {
    status: appliedFilters.status || undefined,
    type: appliedFilters.type || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const reportsQuery = usePortfolioReports(params, canReadReports)
  const exportReports = useExportPortfolioReports()

  const exportParams: PortfolioReportExportQuery = {
    status: appliedFilters.status || undefined,
    type: appliedFilters.type || undefined,
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
          <h1>Reporte de portafolios</h1>
          <p className="app__description">
            Consulta la composición financiera, valuación y rendimiento consolidado de tus
            portafolios.
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
            <p>Refina el reporte por estado y tipo de portafolio.</p>
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
                  status: event.target.value as PortfolioStatus | '',
                }))
              }
            >
              <option value="">Todos</option>
              <option value="ACTIVO">Activo</option>
              <option value="CERRADO">Cerrado</option>
              <option value="ARCHIVADO">Archivado</option>
            </select>
          </label>

          <label className="reporting-field">
            <span>Tipo</span>
            <select
              value={draftFilters.type}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  type: event.target.value as PortfolioType | '',
                }))
              }
            >
              <option value="">Todos</option>
              <option value="VIRTUAL">Virtual</option>
              <option value="SIMULADO">Simulado</option>
            </select>
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
            <h2>Portafolios consolidados</h2>
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
          <PageLoadingState message="Cargando reporte de portafolios..." />
        ) : reportsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar el reporte de portafolios"
            message={reportsQuery.error.message}
            onRetry={() => {
              void reportsQuery.refetch()
            }}
          />
        ) : reports.length === 0 ? (
          <PageEmptyState
            title="No se encontraron portafolios"
            description="No existen portafolios que coincidan con los filtros seleccionados."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="reporting-table-wrapper">
              <table className="reporting-table reporting-table--portfolio">
                <thead>
                  <tr>
                    <th>Portafolio</th>
                    <th>Tipo / Estado</th>
                    <th>Capital invertido</th>
                    <th>Valor actual</th>
                    <th>Ganancia / pérdida</th>
                    <th>Rendimiento</th>
                    <th>Posiciones</th>
                    <th>Última valuación</th>
                  </tr>
                </thead>

                <tbody>
                  {reports.map((report, index) => (
                    <tr
                      key={
                        report.portfolio_id ?? `${report.portfolio_name ?? 'portfolio'}-${index}`
                      }
                    >
                      <td>
                        <strong>{report.portfolio_name ?? 'Sin nombre'}</strong>
                        <span>{report.base_currency ?? 'Moneda no disponible'}</span>
                      </td>

                      <td>
                        <strong>{formatPortfolioType(report.type)}</strong>
                        <span>{formatPortfolioStatus(report.status)}</span>
                      </td>

                      <td>{formatReportCurrency(report.invested_capital, report.base_currency)}</td>

                      <td>{formatReportCurrency(report.positions_value, report.base_currency)}</td>

                      <td className={getFinancialToneClass(report.positions_profit_loss)}>
                        {formatReportCurrency(report.positions_profit_loss, report.base_currency)}
                      </td>

                      <td className={getFinancialToneClass(report.estimated_return_percentage)}>
                        {formatPercentage(report.estimated_return_percentage)}
                      </td>

                      <td>
                        <strong>{report.open_positions ?? 0} abiertas</strong>
                        <span>{report.total_positions ?? 0} totales</span>
                      </td>

                      <td>
                        <strong>{report.last_valuation_at ?? 'No disponible'}</strong>
                        <span>{report.last_valuation_at ? 'Registrada' : 'Sin valuación'}</span>
                      </td>
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
