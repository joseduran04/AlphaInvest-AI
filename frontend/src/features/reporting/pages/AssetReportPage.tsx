import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type { AssetReportExportQuery, AssetReportListQuery } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useAssetTypes } from '@/features/market/hooks/useAssetTypes'
import { useMarkets } from '@/features/market/hooks/useMarkets'
import { useAssetReports } from '@/features/reporting/hooks/useAssetReports'
import { useExportAssetReports } from '@/features/reporting/hooks/useExportAssetReports'
import { formatCurrency } from '@/lib/formatters'

import '@/styles/reporting.css'

const PAGE_SIZE = 20

interface AssetReportFilters {
  symbol: string
  marketCode: string
  assetTypeCode: string
  sector: string
  status: string
}

const initialFilters: AssetReportFilters = {
  symbol: '',
  marketCode: '',
  assetTypeCode: '',
  sector: '',
  status: '',
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

function formatPriceAge(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  if (value === 0) {
    return 'Actualizado hoy'
  }

  return value === 1 ? 'Hace 1 día' : `Hace ${value} días`
}

export function AssetReportPage() {
  const { hasPermission } = useAuth()

  const canReadReports = hasPermission('reportes.leer')
  const canExportReports = hasPermission('reportes.exportar')
  const canReadAssets = hasPermission('activos.leer')

  const [draftFilters, setDraftFilters] = useState<AssetReportFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<AssetReportFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const params: AssetReportListQuery = {
    symbol: appliedFilters.symbol || undefined,
    market_code: appliedFilters.marketCode || undefined,
    asset_type_code: appliedFilters.assetTypeCode || undefined,
    sector: appliedFilters.sector || undefined,
    status: appliedFilters.status || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const reportsQuery = useAssetReports(params, canReadReports)
  const exportReports = useExportAssetReports()

  const exportParams: AssetReportExportQuery = {
    symbol: appliedFilters.symbol || undefined,
    market_code: appliedFilters.marketCode || undefined,
    asset_type_code: appliedFilters.assetTypeCode || undefined,
    sector: appliedFilters.sector || undefined,
    status: appliedFilters.status || undefined,
    limit: 5000,
    offset: 0,
  }
  const marketsQuery = useMarkets({}, canReadReports && canReadAssets)
  const assetTypesQuery = useAssetTypes({}, canReadReports && canReadAssets)

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

    setAppliedFilters({
      ...draftFilters,
      symbol: draftFilters.symbol.trim().toUpperCase(),
      sector: draftFilters.sector.trim(),
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
    <section className="reporting-page">
      <header className="reporting-page__header">
        <div>
          <p className="app__eyebrow">Reportes</p>
          <h1>Reporte de activos</h1>
          <p className="app__description">
            Consulta información consolidada de activos, mercados, precios y fuentes financieras.
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
            <p>Refina el reporte utilizando los criterios disponibles.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="reporting-filters__grid">
          <label className="reporting-field">
            <span>Símbolo</span>
            <input
              type="search"
              value={draftFilters.symbol}
              placeholder="Ej. AAPL"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  symbol: event.target.value,
                }))
              }
            />
          </label>

          <label className="reporting-field">
            <span>Mercado</span>
            <select
              value={draftFilters.marketCode}
              disabled={!canReadAssets || marketsQuery.isPending || marketsQuery.isError}
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

          <label className="reporting-field">
            <span>Tipo de activo</span>
            <select
              value={draftFilters.assetTypeCode}
              disabled={!canReadAssets || assetTypesQuery.isPending || assetTypesQuery.isError}
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

          <label className="reporting-field">
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

          <label className="reporting-field">
            <span>Estado</span>
            <select
              value={draftFilters.status}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  status: event.target.value,
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

        {!canReadAssets ? (
          <p className="reporting-filters__notice">
            Los catálogos de mercado y tipo de activo requieren permiso para consultar activos.
          </p>
        ) : null}

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
            <h2>Activos consolidados</h2>
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
          <PageLoadingState message="Cargando reporte de activos..." />
        ) : reportsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar el reporte de activos"
            message={reportsQuery.error.message}
            onRetry={() => {
              void reportsQuery.refetch()
            }}
          />
        ) : reports.length === 0 ? (
          <PageEmptyState
            title="No se encontraron activos"
            description="No existen registros que coincidan con los filtros seleccionados."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="reporting-table-wrapper">
              <table className="reporting-table">
                <thead>
                  <tr>
                    <th>Activo</th>
                    <th>Mercado</th>
                    <th>Tipo</th>
                    <th>Sector</th>
                    <th>Último precio</th>
                    <th>Variación diaria</th>
                    <th>Fecha precio</th>
                    <th>Fuente</th>
                    <th>Antigüedad</th>
                  </tr>
                </thead>

                <tbody>
                  {reports.map((report) => (
                    <tr key={report.asset_id}>
                      <td>
                        <strong>{report.symbol}</strong>
                        <span>{report.asset_name}</span>
                      </td>
                      <td>
                        <strong>{report.market_code}</strong>
                        <span>{report.market_name}</span>
                      </td>
                      <td>{report.asset_type_name}</td>
                      <td>{report.sector ?? 'No disponible'}</td>
                      <td>
                        {report.currency
                          ? formatCurrency(report.close_price, report.currency)
                          : (report.close_price ?? 'No disponible')}
                      </td>
                      <td>{formatPercentage(report.daily_change_percentage)}</td>
                      <td>{report.price_date ?? 'No disponible'}</td>
                      <td>{report.source_name ?? 'No disponible'}</td>
                      <td>{formatPriceAge(report.price_age_days)}</td>
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
