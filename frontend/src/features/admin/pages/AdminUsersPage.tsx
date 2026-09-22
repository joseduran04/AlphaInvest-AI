import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type { UserReportExportQuery, UserReportListQuery } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useExportUserReports } from '@/features/reporting/hooks/useExportUserReports'
import { useUserReports } from '@/features/reporting/hooks/useUserReports'

import '@/styles/admin.css'

const PAGE_SIZE = 20

type BooleanFilter = '' | 'true' | 'false'

interface AdminUserFilters {
  status: string
  emailVerified: BooleanFilter
  blocked: BooleanFilter
}

const initialFilters: AdminUserFilters = {
  status: '',
  emailVerified: '',
  blocked: '',
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

function formatRoles(roles: string[] | null | undefined): string {
  if (!roles || roles.length === 0) {
    return 'Sin roles'
  }

  return roles.join(', ')
}

export function AdminUsersPage() {
  const { hasPermission } = useAuth()

  const canManageReports = hasPermission('reportes.administrar')
  const canExportReports = hasPermission('reportes.exportar')

  const [draftFilters, setDraftFilters] = useState<AdminUserFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<AdminUserFilters>(initialFilters)
  const [page, setPage] = useState(0)

  const params: UserReportListQuery = {
    status: appliedFilters.status.trim() || undefined,
    email_verified: toOptionalBoolean(appliedFilters.emailVerified),
    blocked: toOptionalBoolean(appliedFilters.blocked),
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const reportsQuery = useUserReports(params, canManageReports)
  const exportReports = useExportUserReports()

  const exportParams: UserReportExportQuery = {
    status: appliedFilters.status.trim() || undefined,
    email_verified: toOptionalBoolean(appliedFilters.emailVerified),
    blocked: toOptionalBoolean(appliedFilters.blocked),
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
      ...draftFilters,
      status: draftFilters.status.trim(),
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
          <h1>Usuarios</h1>
          <p className="app__description">
            Consulta el estado, acceso, bloqueos y roles de los usuarios registrados.
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
            <p>Refina el reporte administrativo utilizando los criterios disponibles.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="admin-filters__grid">
          <label className="admin-field">
            <span>Estado</span>
            <input
              type="text"
              value={draftFilters.status}
              placeholder="Ej. ACTIVO"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  status: event.target.value,
                }))
              }
            />
          </label>

          <label className="admin-field">
            <span>Correo verificado</span>
            <select
              value={draftFilters.emailVerified}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  emailVerified: event.target.value as BooleanFilter,
                }))
              }
            >
              <option value="">Todos</option>
              <option value="true">Sí</option>
              <option value="false">No</option>
            </select>
          </label>

          <label className="admin-field">
            <span>Bloqueado actualmente</span>
            <select
              value={draftFilters.blocked}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  blocked: event.target.value as BooleanFilter,
                }))
              }
            >
              <option value="">Todos</option>
              <option value="true">Sí</option>
              <option value="false">No</option>
            </select>
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
            <h2>Usuarios registrados</h2>
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
          <PageLoadingState message="Cargando reporte administrativo de usuarios..." />
        ) : reportsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar los usuarios"
            message={reportsQuery.error.message}
            onRetry={() => {
              void reportsQuery.refetch()
            }}
          />
        ) : reports.length === 0 ? (
          <PageEmptyState
            title="No se encontraron usuarios"
            description="No existen registros que coincidan con los filtros seleccionados."
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
                    <th>Usuario</th>
                    <th>Estado</th>
                    <th>Correo verificado</th>
                    <th>Roles</th>
                    <th>Intentos fallidos</th>
                    <th>Bloqueado</th>
                    <th>Último acceso</th>
                    <th>Creación</th>
                  </tr>
                </thead>

                <tbody>
                  {reports.map((report) => (
                    <tr key={report.user_id ?? report.email ?? undefined}>
                      <td>
                        <strong>
                          {[report.first_names, report.last_names].filter(Boolean).join(' ') ||
                            'Sin nombre'}
                        </strong>
                        <span>{report.email ?? 'Sin correo'}</span>
                      </td>
                      <td>{report.status ?? 'No disponible'}</td>
                      <td>{formatBoolean(report.email_verified)}</td>
                      <td>{formatRoles(report.roles)}</td>
                      <td>{report.failed_attempts ?? 'No disponible'}</td>
                      <td>{formatBoolean(report.currently_blocked)}</td>
                      <td>{formatDateTime(report.last_access_at)}</td>
                      <td>{formatDateTime(report.created_at)}</td>
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
