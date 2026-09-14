import { useState } from 'react'
import { Link } from 'react-router'

import type { PortfolioListQuery, PortfolioStatus } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { CreatePortfolioForm } from '@/features/portfolio/components/CreatePortfolioForm'
import { usePortfolios } from '@/features/portfolio/hooks/usePortfolios'
import { formatCurrency } from '@/lib/formatters'

import '@/styles/portfolio.css'

const PAGE_SIZE = 20

function formatPortfolioStatus(status: PortfolioStatus): string {
  switch (status) {
    case 'ACTIVO':
      return 'Activo'
    case 'CERRADO':
      return 'Cerrado'
    case 'ARCHIVADO':
      return 'Archivado'
  }
}

function formatPortfolioType(type: 'VIRTUAL' | 'SIMULADO'): string {
  switch (type) {
    case 'VIRTUAL':
      return 'Virtual'
    case 'SIMULADO':
      return 'Simulado'
  }
}

export function PortfoliosPage() {
  const { hasPermission } = useAuth()

  const canReadPortfolios = hasPermission('portafolios.leer')
  const canCreatePortfolios = hasPermission('portafolios.crear')

  const [status, setStatus] = useState<PortfolioStatus | ''>('')
  const [page, setPage] = useState(0)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const params: PortfolioListQuery = {
    estado: status || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const portfoliosQuery = usePortfolios(params, canReadPortfolios)

  if (!canReadPortfolios) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar portafolios."
      />
    )
  }

  const portfolios = portfoliosQuery.data?.items ?? []
  const total = portfoliosQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const firstResult = total === 0 ? 0 : page * PAGE_SIZE + 1
  const lastResult = Math.min((page + 1) * PAGE_SIZE, total)

  function handleStatusChange(nextStatus: PortfolioStatus | '') {
    setStatus(nextStatus)
    setPage(0)
  }

  return (
    <section className="portfolio-page">
      <header className="portfolio-page__header">
        <div>
          <p className="app__eyebrow">Portafolios</p>
          <h1>Mis portafolios</h1>
          <p className="app__description">
            Consulta y administra los portafolios registrados en AlphaInvest AI.
          </p>
        </div>

        {canCreatePortfolios && !showCreateForm ? (
          <button
            className="button button--primary"
            type="button"
            onClick={() => setShowCreateForm(true)}
          >
            Crear portafolio
          </button>
        ) : null}
      </header>

      {canCreatePortfolios && showCreateForm ? (
        <CreatePortfolioForm
          onCancel={() => setShowCreateForm(false)}
          onCreated={() => setShowCreateForm(false)}
        />
      ) : null}

      <section className="portfolio-filters">
        <header className="portfolio-filters__header">
          <div>
            <h2>Filtros</h2>
            <p>Filtra los portafolios utilizando los criterios disponibles.</p>
          </div>
        </header>

        <div className="portfolio-filters__grid">
          <label className="portfolio-field">
            <span>Estado</span>
            <select
              value={status}
              onChange={(event) => handleStatusChange(event.target.value as PortfolioStatus | '')}
            >
              <option value="">Todos</option>
              <option value="ACTIVO">Activo</option>
              <option value="CERRADO">Cerrado</option>
              <option value="ARCHIVADO">Archivado</option>
            </select>
          </label>
        </div>
      </section>

      <section className="portfolio-results">
        <header className="portfolio-results__header">
          <div>
            <p className="portfolio-results__eyebrow">Resultados</p>
            <h2>Portafolios registrados</h2>
          </div>

          {!portfoliosQuery.isPending && !portfoliosQuery.isError ? (
            <span className="portfolio-results__count">{total} registros</span>
          ) : null}
        </header>

        {portfoliosQuery.isPending ? (
          <PageLoadingState message="Cargando portafolios..." />
        ) : portfoliosQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar los portafolios"
            message={portfoliosQuery.error.message}
            onRetry={() => {
              void portfoliosQuery.refetch()
            }}
          />
        ) : portfolios.length === 0 ? (
          <PageEmptyState
            title="No se encontraron portafolios"
            description={
              status
                ? 'No existen portafolios con el estado seleccionado.'
                : 'Todavía no existen portafolios registrados.'
            }
            action={
              status ? (
                <button
                  className="button button--secondary"
                  type="button"
                  onClick={() => handleStatusChange('')}
                >
                  Mostrar todos
                </button>
              ) : canCreatePortfolios ? (
                <button
                  className="button button--primary"
                  type="button"
                  onClick={() => setShowCreateForm(true)}
                >
                  Crear portafolio
                </button>
              ) : undefined
            }
          />
        ) : (
          <>
            <div className="portfolio-cards">
              {portfolios.map((portfolio) => (
                <article className="portfolio-card" key={portfolio.id}>
                  <header className="portfolio-card__header">
                    <div>
                      <strong>{portfolio.nombre}</strong>
                      <span>{formatPortfolioType(portfolio.tipo)}</span>
                    </div>

                    <span
                      className={`portfolio-status portfolio-status--${portfolio.estado.toLowerCase()}`}
                    >
                      {formatPortfolioStatus(portfolio.estado)}
                    </span>
                  </header>

                  {portfolio.descripcion ? (
                    <p className="portfolio-card__description">{portfolio.descripcion}</p>
                  ) : null}

                  <dl className="portfolio-card__details">
                    <div>
                      <dt>Capital inicial</dt>
                      <dd>{formatCurrency(portfolio.capital_inicial, portfolio.moneda_base)}</dd>
                    </div>

                    <div>
                      <dt>Saldo efectivo</dt>
                      <dd>{formatCurrency(portfolio.saldo_efectivo, portfolio.moneda_base)}</dd>
                    </div>

                    <div>
                      <dt>Moneda base</dt>
                      <dd>{portfolio.moneda_base}</dd>
                    </div>

                    <div>
                      <dt>Fecha de inicio</dt>
                      <dd>{portfolio.fecha_inicio}</dd>
                    </div>
                  </dl>

                  <Link
                    className="button button--secondary portfolio-card__action"
                    to={`/app/portfolios/${portfolio.id}`}
                  >
                    Ver detalle
                  </Link>
                </article>
              ))}
            </div>

            <footer className="portfolio-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="portfolio-pagination__controls">
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
