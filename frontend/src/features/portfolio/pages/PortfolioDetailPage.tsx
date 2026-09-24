import { useState } from 'react'
import { Link, useParams } from 'react-router'

import { ApiError } from '@/api/errors'
import type { PortfolioStatus } from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'

import { useAssets } from '@/features/market/hooks/useAssets'
import { CreatePositionForm } from '@/features/portfolio/components/CreatePositionForm'
import { ClosePortfolioSection } from '@/features/portfolio/components/ClosePortfolioSection'
import { PositionCard } from '@/features/portfolio/components/PositionCard'
import { PortfolioAllocationSection } from '@/features/portfolio/components/PortfolioAllocationSection'
import { PortfolioValuationsSection } from '@/features/portfolio/components/PortfolioValuationsSection'
import { EditPortfolioForm } from '@/features/portfolio/components/EditPortfolioForm'
import { usePortfolio } from '@/features/portfolio/hooks/usePortfolio'
import { usePortfolioPositions } from '@/features/portfolio/hooks/usePortfolioPositions'
import { usePortfolioSummary } from '@/features/portfolio/hooks/usePortfolioSummary'
import { getFinancialToneClass } from '@/lib/financialTone'
import { formatCurrency } from '@/lib/formatters'

import '@/styles/portfolio.css'

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

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  const dateOnlyMatch = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)

  if (dateOnlyMatch) {
    const [, year, month, day] = dateOnlyMatch
    const date = new Date(Number(year), Number(month) - 1, Number(day))

    return new Intl.DateTimeFormat('es-MX', {
      dateStyle: 'medium',
    }).format(date)
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

function formatPercentage(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}

function isNotFoundError(error: Error | null): boolean {
  return error instanceof ApiError && error.status === 404
}

export function PortfolioDetailPage() {
  const { portfolioId } = useParams<{ portfolioId: string }>()
  const { hasPermission } = useAuth()

  const [showEditForm, setShowEditForm] = useState(false)

  const [showCreatePositionForm, setShowCreatePositionForm] = useState(false)

  const normalizedPortfolioId = portfolioId ?? null
  const canUpdatePortfolio = hasPermission('portafolios.actualizar')
  const canClosePortfolio = hasPermission('portafolios.cerrar')

  const portfolioQuery = usePortfolio(normalizedPortfolioId)
  const summaryQuery = usePortfolioSummary(normalizedPortfolioId)

  const positionsQuery = usePortfolioPositions(normalizedPortfolioId)

  const assetsQuery = useAssets({}, normalizedPortfolioId !== null)

  if (!normalizedPortfolioId) {
    return (
      <PageErrorState
        title="Portafolio no válido"
        message="No se proporcionó un identificador de portafolio válido."
      />
    )
  }

  if (portfolioQuery.isPending || summaryQuery.isPending) {
    return <PageLoadingState message="Cargando detalle del portafolio..." />
  }

  if (portfolioQuery.isError || summaryQuery.isError) {
    const portfolioError = portfolioQuery.error
    const summaryError = summaryQuery.error

    if (isNotFoundError(portfolioError) || isNotFoundError(summaryError)) {
      return (
        <PageErrorState
          title="Portafolio no encontrado"
          message="El portafolio solicitado no existe o no está disponible."
        />
      )
    }

    return (
      <PageErrorState
        title="No fue posible cargar el portafolio"
        message={
          portfolioError?.message ??
          summaryError?.message ??
          'No fue posible consultar el detalle del portafolio.'
        }
        onRetry={() => {
          void Promise.all([portfolioQuery.refetch(), summaryQuery.refetch()])
        }}
      />
    )
  }

  const portfolio = portfolioQuery.data
  const overview = summaryQuery.data
  const summary = overview.resumen
  const latestValuation = overview.ultima_valoracion

  const isActivePortfolio = portfolio.estado === 'ACTIVO'
  const canMutatePortfolio = canUpdatePortfolio && isActivePortfolio

  const assetsById = new Map((assetsQuery.data?.items ?? []).map((asset) => [asset.id, asset]))

  return (
    <section className="portfolio-detail-page">
      <nav className="portfolio-detail-page__navigation" aria-label="Navegación de portafolio">
        <Link className="portfolio-detail-page__back" to="/app/portfolios">
          ← Volver a portafolios
        </Link>
      </nav>

      <header className="portfolio-detail-page__header">
        <div>
          <p className="app__eyebrow">Portafolio</p>
          <h1>{portfolio.nombre}</h1>
          <p className="app__description">
            Consulta el estado y las métricas financieras actuales del portafolio.
          </p>
        </div>

        <div className="portfolio-detail-page__header-actions">
          <span className={`portfolio-status portfolio-status--${portfolio.estado.toLowerCase()}`}>
            {formatPortfolioStatus(portfolio.estado)}
          </span>

          {canMutatePortfolio && !showEditForm ? (
            <button
              className="button button--secondary"
              type="button"
              onClick={() => setShowEditForm(true)}
            >
              Editar portafolio
            </button>
          ) : null}
        </div>
      </header>

      {showEditForm && canMutatePortfolio ? (
        <EditPortfolioForm
          portfolioId={portfolio.id}
          portfolio={portfolio}
          onCancel={() => setShowEditForm(false)}
          onUpdated={() => setShowEditForm(false)}
        />
      ) : null}

      <section className="portfolio-detail-section">
        <header className="portfolio-detail-section__header">
          <div>
            <p className="portfolio-results__eyebrow">Información general</p>
            <h2>Datos del portafolio</h2>
          </div>
        </header>

        <dl className="portfolio-detail-grid">
          <div>
            <dt>Tipo</dt>
            <dd>{formatPortfolioType(portfolio.tipo)}</dd>
          </div>

          <div>
            <dt>Moneda base</dt>
            <dd>{portfolio.moneda_base}</dd>
          </div>

          <div>
            <dt>Fecha de inicio</dt>
            <dd>{formatDate(portfolio.fecha_inicio)}</dd>
          </div>

          <div>
            <dt>Fecha de cierre</dt>
            <dd>{formatDate(portfolio.fecha_cierre)}</dd>
          </div>

          <div>
            <dt>Creado</dt>
            <dd>{formatDate(portfolio.fecha_creacion)}</dd>
          </div>

          <div>
            <dt>Última actualización</dt>
            <dd>{formatDate(portfolio.fecha_actualizacion)}</dd>
          </div>
        </dl>

        <div className="portfolio-detail-description">
          <span>Descripción</span>
          <p>{portfolio.descripcion || 'Sin descripción registrada.'}</p>
        </div>
      </section>

      <section className="portfolio-detail-section">
        <header className="portfolio-detail-section__header">
          <div>
            <p className="portfolio-results__eyebrow">Resumen financiero</p>
            <h2>Situación actual</h2>
          </div>
        </header>

        <div className="portfolio-metrics">
          <article className="portfolio-metric-card">
            <span>Capital invertido</span>
            <strong>{formatCurrency(summary.capital_invertido, summary.moneda_base)}</strong>
          </article>

          <article className="portfolio-metric-card">
            <span>Valor actual</span>
            <strong>{formatCurrency(summary.valor_posiciones, summary.moneda_base)}</strong>
          </article>

          <article className="portfolio-metric-card">
            <span>Ganancia / pérdida</span>
            <strong className={getFinancialToneClass(summary.ganancia_perdida_total)}>
              {formatCurrency(summary.ganancia_perdida_total, summary.moneda_base)}
            </strong>
          </article>

          <article className="portfolio-metric-card">
            <span>Rendimiento sobre lo invertido</span>
            <strong className={getFinancialToneClass(summary.rendimiento_estimado_porcentaje)}>
              {formatPercentage(summary.rendimiento_estimado_porcentaje)}
            </strong>
          </article>

          <article className="portfolio-metric-card">
            <span>Posiciones abiertas</span>
            <strong>{summary.posiciones_abiertas}</strong>
          </article>

          <article className="portfolio-metric-card">
            <span>Posiciones totales</span>
            <strong>{summary.posiciones_totales}</strong>
          </article>
        </div>
      </section>

      <section className="portfolio-detail-section">
        <header className="portfolio-detail-section__header">
          <div>
            <p className="portfolio-results__eyebrow">Posiciones</p>
            <h2>Posiciones del portafolio</h2>
          </div>

          {canMutatePortfolio && !showCreatePositionForm ? (
            <button
              className="button button--primary"
              type="button"
              onClick={() => setShowCreatePositionForm(true)}
            >
              Agregar posición
            </button>
          ) : null}
        </header>

        {showCreatePositionForm && canMutatePortfolio ? (
          <CreatePositionForm
            portfolioId={portfolio.id}
            onCancel={() => setShowCreatePositionForm(false)}
            onCreated={() => setShowCreatePositionForm(false)}
          />
        ) : null}

        {positionsQuery.isPending ? (
          <PageLoadingState message="Cargando posiciones..." />
        ) : positionsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar las posiciones"
            message={positionsQuery.error.message}
            onRetry={() => {
              void positionsQuery.refetch()
            }}
          />
        ) : positionsQuery.data.items.length === 0 ? (
          <p className="portfolio-detail-section__empty">
            Todavía no existen posiciones registradas en este portafolio.
          </p>
        ) : (
          <div className="portfolio-position-list">
            {positionsQuery.data.items.map((position) => (
              <PositionCard
                key={position.id}
                portfolioId={portfolio.id}
                position={position}
                asset={assetsById.get(position.activo_id)}
                canUpdate={canMutatePortfolio}
              />
            ))}
          </div>
        )}
      </section>

      <PortfolioAllocationSection portfolioId={portfolio.id} />

      <PortfolioValuationsSection portfolioId={portfolio.id} canCreate={canUpdatePortfolio} />

      <section className="portfolio-detail-section">
        <header className="portfolio-detail-section__header">
          <div>
            <p className="portfolio-results__eyebrow">Última valoración</p>
            <h2>Valoración registrada</h2>
          </div>
        </header>

        {latestValuation ? (
          <dl className="portfolio-detail-grid">
            <div>
              <dt>Fecha</dt>
              <dd>{formatDate(latestValuation.fecha_hora)}</dd>
            </div>

            <div>
              <dt>Capital invertido</dt>
              <dd>{formatCurrency(latestValuation.capital_invertido, latestValuation.moneda)}</dd>
            </div>

            <div>
              <dt>Valor actual</dt>
              <dd>{formatCurrency(latestValuation.valor_posiciones, latestValuation.moneda)}</dd>
            </div>

            <div>
              <dt>Ganancia / pérdida</dt>
              <dd className={getFinancialToneClass(latestValuation.ganancia_perdida)}>
                {formatCurrency(latestValuation.ganancia_perdida, latestValuation.moneda)}
              </dd>
            </div>

            <div>
              <dt>Rendimiento</dt>
              <dd className={getFinancialToneClass(latestValuation.rendimiento_porcentaje)}>
                {formatPercentage(latestValuation.rendimiento_porcentaje)}
              </dd>
            </div>
          </dl>
        ) : (
          <p className="portfolio-detail-section__empty">
            Todavía no existe una valoración registrada para este portafolio.
          </p>
        )}
      </section>
      <ClosePortfolioSection
        portfolioId={portfolio.id}
        status={portfolio.estado}
        openPositions={summary.posiciones_abiertas}
        canClose={canClosePortfolio}
      />
    </section>
  )
}
