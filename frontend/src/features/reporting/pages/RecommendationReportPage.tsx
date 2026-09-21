import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type {
  AnalysisHorizon,
  RecommendationReportExportQuery,
  RecommendationReportListQuery,
} from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useRecommendationReports } from '@/features/reporting/hooks/useRecommendationReports'
import { useExportRecommendationReports } from '@/features/reporting/hooks/useExportRecommendationReports'

import '@/styles/reporting.css'

const PAGE_SIZE = 20

interface RecommendationReportFilters {
  type: string
  riskLevel: string
  horizon: AnalysisHorizon | ''
  status: string
  dateFrom: string
  dateTo: string
}

const initialFilters: RecommendationReportFilters = {
  type: '',
  riskLevel: '',
  horizon: '',
  status: '',
  dateFrom: '',
  dateTo: '',
}

function formatRecommendationType(value: string | null): string {
  switch (value) {
    case 'OBSERVAR':
      return 'Observar'
    case 'COMPRAR_SIMULADO':
      return 'Compra simulada'
    case 'MANTENER':
      return 'Mantener'
    case 'REDUCIR':
      return 'Reducir'
    case 'VENDER_SIMULADO':
      return 'Venta simulada'
    case 'DIVERSIFICAR':
      return 'Diversificar'
    case 'REBALANCEAR':
      return 'Rebalancear'
    case 'EVITAR':
      return 'Evitar'
    default:
      return value ?? 'No disponible'
  }
}

function formatCodeValue(value: string | null): string {
  if (!value) {
    return 'No disponible'
  }

  return value.replaceAll('_', ' ').toLocaleLowerCase('es-MX')
}

function formatProbability(value: string | number | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return 'No disponible'
  }

  return `${(numericValue * 100).toFixed(2)} %`
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function RecommendationReportPage() {
  const { hasPermission } = useAuth()

  const canReadReports = hasPermission('reportes.leer')
  const canExportReports = hasPermission('reportes.exportar')

  const [draftFilters, setDraftFilters] = useState<RecommendationReportFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<RecommendationReportFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const params: RecommendationReportListQuery = {
    type: appliedFilters.type || undefined,
    risk_level: appliedFilters.riskLevel || undefined,
    horizon: appliedFilters.horizon || undefined,
    status: appliedFilters.status || undefined,
    date_from: appliedFilters.dateFrom || undefined,
    date_to: appliedFilters.dateTo || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const reportsQuery = useRecommendationReports(params, canReadReports)
  const exportReports = useExportRecommendationReports()

  const exportParams: RecommendationReportExportQuery = {
    type: appliedFilters.type || undefined,
    risk_level: appliedFilters.riskLevel || undefined,
    horizon: appliedFilters.horizon || undefined,
    status: appliedFilters.status || undefined,
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
          <h1>Reporte de recomendaciones</h1>
          <p className="app__description">
            Consulta las recomendaciones generadas por AlphaInvest AI y su contexto consolidado.
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
            <p>Refina el reporte por tipo, riesgo, horizonte, estado y fecha de generación.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="reporting-filters__grid">
          <label className="reporting-field">
            <span>Tipo</span>
            <select
              value={draftFilters.type}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  type: event.target.value,
                }))
              }
            >
              <option value="">Todos</option>
              <option value="OBSERVAR">Observar</option>
              <option value="COMPRAR_SIMULADO">Compra simulada</option>
              <option value="MANTENER">Mantener</option>
              <option value="REDUCIR">Reducir</option>
              <option value="VENDER_SIMULADO">Venta simulada</option>
              <option value="DIVERSIFICAR">Diversificar</option>
              <option value="REBALANCEAR">Rebalancear</option>
              <option value="EVITAR">Evitar</option>
            </select>
          </label>

          <label className="reporting-field">
            <span>Nivel de riesgo</span>
            <input
              type="text"
              value={draftFilters.riskLevel}
              placeholder="Ej. MODERADO"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  riskLevel: event.target.value,
                }))
              }
            />
          </label>

          <label className="reporting-field">
            <span>Horizonte</span>
            <select
              value={draftFilters.horizon}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  horizon: event.target.value as AnalysisHorizon | '',
                }))
              }
            >
              <option value="">Todos</option>
              <option value="INTRADIA">Intradía</option>
              <option value="CORTO_PLAZO">Corto plazo</option>
              <option value="MEDIANO_PLAZO">Mediano plazo</option>
              <option value="LARGO_PLAZO">Largo plazo</option>
            </select>
          </label>

          <label className="reporting-field">
            <span>Estado</span>
            <input
              type="text"
              value={draftFilters.status}
              placeholder="Estado"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  status: event.target.value,
                }))
              }
            />
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
            <h2>Recomendaciones consolidadas</h2>
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
          <PageLoadingState message="Cargando reporte de recomendaciones..." />
        ) : reportsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar el reporte de recomendaciones"
            message={reportsQuery.error.message}
            onRetry={() => {
              void reportsQuery.refetch()
            }}
          />
        ) : reports.length === 0 ? (
          <PageEmptyState
            title="No se encontraron recomendaciones"
            description="No existen recomendaciones que coincidan con los filtros seleccionados."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="reporting-table-wrapper">
              <table className="reporting-table reporting-table--recommendation">
                <thead>
                  <tr>
                    <th>Recomendación</th>
                    <th>Tipo</th>
                    <th>Riesgo / Horizonte</th>
                    <th>Confianza</th>
                    <th>Prioridad</th>
                    <th>Estado</th>
                    <th>Portafolio</th>
                    <th>Activos</th>
                    <th>Modelo</th>
                    <th>Generada</th>
                    <th>Vigencia</th>
                  </tr>
                </thead>

                <tbody>
                  {reports.map((report, index) => (
                    <tr
                      key={
                        report.recommendation_id ??
                        `${report.request_id ?? 'recommendation'}-${index}`
                      }
                    >
                      <td>
                        <strong>{report.title ?? 'Sin título'}</strong>
                        <span>{report.summary ?? 'Sin resumen'}</span>
                      </td>

                      <td>{formatRecommendationType(report.type)}</td>

                      <td>
                        <strong>{formatCodeValue(report.risk_level)}</strong>
                        <span>{formatCodeValue(report.horizon)}</span>
                      </td>

                      <td>{formatProbability(report.confidence)}</td>

                      <td>{report.priority ?? 'No disponible'}</td>

                      <td>
                        <strong>{formatCodeValue(report.status)}</strong>
                        <span>
                          {report.expired_by_date ? 'Vencida por fecha' : 'Vigente por fecha'}
                        </span>
                      </td>

                      <td>{report.portfolio_name ?? 'Sin portafolio'}</td>

                      <td>
                        <strong>{report.related_asset_count ?? 0} relacionados</strong>
                        <span>
                          {report.asset_symbols?.length
                            ? report.asset_symbols.join(', ')
                            : 'Sin activos'}
                        </span>
                      </td>

                      <td>
                        <strong>{report.model_name ?? 'No disponible'}</strong>
                        <span>
                          {report.model_version
                            ? `v${report.model_version}`
                            : 'Versión no disponible'}
                        </span>
                      </td>

                      <td>{formatDateTime(report.generated_at)}</td>

                      <td>
                        <strong>{formatDateTime(report.expires_at)}</strong>
                        <span>
                          {report.accepted_at
                            ? `Aceptada: ${formatDateTime(report.accepted_at)}`
                            : report.rejected_at
                              ? `Rechazada: ${formatDateTime(report.rejected_at)}`
                              : 'Sin resolución'}
                        </span>
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
