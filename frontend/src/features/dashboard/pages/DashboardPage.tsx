import { Link } from 'react-router'

import { DashboardPanelState } from '@/features/dashboard/components/DashboardPanelState'
import { useDashboardAssets } from '@/features/dashboard/hooks/useDashboardAssets'
import { useDashboardPortfolioOverview } from '@/features/dashboard/hooks/useDashboardPortfolioOverview'
import { useDashboardPortfolios } from '@/features/dashboard/hooks/useDashboardPortfolios'
import { useDashboardRecommendations } from '@/features/dashboard/hooks/useDashboardRecommendations'
import { useDashboardSimulationExecutions } from '@/features/dashboard/hooks/useDashboardSimulationExecutions'
import {
  formatDashboardDate,
  formatDashboardLabel,
  formatDashboardMoney,
  formatDashboardPercentage,
} from '@/features/dashboard/utils/dashboardFormatters'
import { getFinancialToneClass } from '@/lib/financialTone'
import { useNotifications } from '@/features/notifications/hooks/useNotifications'
import { useUnreadNotificationCount } from '@/features/notifications/hooks/useUnreadNotificationCount'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useCurrentRiskProfile } from '@/features/profile/hooks/useCurrentRiskProfile'
import {
  formatRiskClassification,
  formatRiskScore,
} from '@/features/profile/utils/profileFormatters'

import '@/styles/dashboard.css'

export function DashboardPage() {
  const { user, hasPermission } = useAuth()

  const canReadPortfolios = hasPermission('portafolios.leer')
  const canReadSimulations = hasPermission('simulaciones.leer')
  const canReadNotifications = hasPermission('notificaciones.leer')
  const canReadReports = hasPermission('reportes.leer')
  const canReadAssets = hasPermission('activos.leer')

  const profileQuery = useCurrentRiskProfile()

  const portfoliosQuery = useDashboardPortfolios(canReadPortfolios)
  const simulationsQuery = useDashboardSimulationExecutions(canReadSimulations)
  const unreadNotificationsQuery = useUnreadNotificationCount(canReadNotifications)
  const notificationsQuery = useNotifications(
    {
      unread_only: false,
      limit: 5,
      offset: 0,
    },
    canReadNotifications,
  )
  const recommendationsQuery = useDashboardRecommendations(canReadReports)
  const assetsQuery = useDashboardAssets(canReadAssets)

  const selectedPortfolioId = portfoliosQuery.data?.items[0]?.id ?? null

  const portfolioOverviewQuery = useDashboardPortfolioOverview(
    selectedPortfolioId,
    canReadPortfolios,
  )

  const profile = profileQuery.data
  const portfolioOverview = portfolioOverviewQuery.data
  const portfolioSummary = portfolioOverview?.resumen

  return (
    <section className="dashboard-page">
      <header className="dashboard-page__header">
        <div>
          <p className="app__eyebrow">Panel principal</p>
          <h1>Bienvenido, {user?.nombres}</h1>
          <p className="app__description">
            Consulta el estado general de tu cuenta y accede a las capacidades disponibles para tu
            usuario en AlphaInvest AI.
          </p>
        </div>

        {canReadReports ? (
          <Link className="button button--secondary" to="/app/reports">
            Centro de reportes
          </Link>
        ) : null}
      </header>

      <section className="dashboard-kpis" aria-label="Resumen general">
        <article className="dashboard-kpi">
          <span className="dashboard-kpi__label">Perfil de riesgo</span>

          {profileQuery.isPending ? (
            <span className="dashboard-kpi__value">Cargando...</span>
          ) : profileQuery.isError ? (
            <span className="dashboard-kpi__value">No disponible</span>
          ) : profile ? (
            <>
              <strong className="dashboard-kpi__value">
                {formatRiskClassification(profile.classification)}
              </strong>
              <span className="dashboard-kpi__meta">{formatRiskScore(profile.score)}</span>
            </>
          ) : (
            <>
              <strong className="dashboard-kpi__value">Sin evaluar</strong>
              <Link className="dashboard-kpi__link" to="/app/profile">
                Completar perfil
              </Link>
            </>
          )}
        </article>

        {canReadPortfolios ? (
          <article className="dashboard-kpi">
            <span className="dashboard-kpi__label">Portafolios activos</span>

            {portfoliosQuery.isPending ? (
              <strong className="dashboard-kpi__value">Cargando...</strong>
            ) : portfoliosQuery.isError ? (
              <strong className="dashboard-kpi__value">No disponible</strong>
            ) : (
              <strong className="dashboard-kpi__value">{portfoliosQuery.data.total}</strong>
            )}
          </article>
        ) : null}

        {canReadSimulations ? (
          <article className="dashboard-kpi">
            <span className="dashboard-kpi__label">Simulaciones</span>

            {simulationsQuery.isPending ? (
              <strong className="dashboard-kpi__value">Cargando...</strong>
            ) : simulationsQuery.isError ? (
              <strong className="dashboard-kpi__value">No disponible</strong>
            ) : (
              <strong className="dashboard-kpi__value">{simulationsQuery.data.total}</strong>
            )}
          </article>
        ) : null}

        {canReadNotifications ? (
          <article className="dashboard-kpi">
            <span className="dashboard-kpi__label">Notificaciones no leídas</span>

            {unreadNotificationsQuery.isPending ? (
              <strong className="dashboard-kpi__value">Cargando...</strong>
            ) : unreadNotificationsQuery.isError ? (
              <strong className="dashboard-kpi__value">No disponible</strong>
            ) : (
              <strong className="dashboard-kpi__value">
                {unreadNotificationsQuery.data.unread}
              </strong>
            )}
          </article>
        ) : null}
      </section>

      <div className="dashboard-grid">
        <article className="dashboard-panel">
          <header className="dashboard-panel__header">
            <div>
              <span className="dashboard-panel__eyebrow">Perfil de riesgo</span>
              <h2>Tu perfil como inversionista</h2>
            </div>
          </header>

          {profileQuery.isPending ? (
            <DashboardPanelState message="Cargando tu perfil de riesgo..." />
          ) : profileQuery.isError ? (
            <DashboardPanelState
              error
              message={profileQuery.error.message}
              onRetry={() => {
                void profileQuery.refetch()
              }}
            />
          ) : profile === null ? (
            <div className="dashboard-panel__empty">
              <p>Todavía no tienes una evaluación de riesgo vigente.</p>

              <Link className="button button--primary" to="/app/profile">
                Evaluar mi perfil
              </Link>
            </div>
          ) : (
            <dl className="dashboard-details">
              <div>
                <dt>Clasificación</dt>
                <dd>{formatRiskClassification(profile.classification)}</dd>
              </div>

              <div>
                <dt>Puntuación</dt>
                <dd>{formatRiskScore(profile.score)}</dd>
              </div>

              <div>
                <dt>Estado</dt>
                <dd>{profile.current ? 'Vigente' : 'No vigente'}</dd>
              </div>
            </dl>
          )}
        </article>

        {canReadPortfolios ? (
          <article className="dashboard-panel">
            <header className="dashboard-panel__header">
              <div>
                <span className="dashboard-panel__eyebrow">Portafolios</span>
                <h2>Portafolio activo</h2>
              </div>
            </header>

            {portfoliosQuery.isPending ? (
              <DashboardPanelState message="Cargando portafolios..." />
            ) : portfoliosQuery.isError ? (
              <DashboardPanelState
                error
                message={portfoliosQuery.error.message}
                onRetry={() => {
                  void portfoliosQuery.refetch()
                }}
              />
            ) : portfoliosQuery.data.items.length === 0 ? (
              <DashboardPanelState message="No tienes portafolios activos." />
            ) : portfolioOverviewQuery.isPending ? (
              <DashboardPanelState message="Cargando resumen del portafolio..." />
            ) : portfolioOverviewQuery.isError ? (
              <DashboardPanelState
                error
                message={portfolioOverviewQuery.error.message}
                onRetry={() => {
                  void portfolioOverviewQuery.refetch()
                }}
              />
            ) : portfolioSummary ? (
              <>
                <div className="dashboard-panel__primary-value">
                  <span>{portfolioSummary.portafolio_nombre}</span>
                  <strong>
                    {formatDashboardMoney(
                      portfolioSummary.valor_total_estimado,
                      portfolioSummary.moneda_base,
                    )}
                  </strong>
                </div>

                <dl className="dashboard-details">
                  <div>
                    <dt>Ganancia / pérdida</dt>
                    <dd className={getFinancialToneClass(portfolioSummary.ganancia_perdida_total)}>
                      {formatDashboardMoney(
                        portfolioSummary.ganancia_perdida_total,
                        portfolioSummary.moneda_base,
                      )}
                    </dd>
                  </div>

                  <div>
                    <dt>Rendimiento</dt>
                    <dd
                      className={getFinancialToneClass(
                        portfolioSummary.rendimiento_estimado_porcentaje,
                      )}
                    >
                      {formatDashboardPercentage(portfolioSummary.rendimiento_estimado_porcentaje)}
                    </dd>
                  </div>

                  <div>
                    <dt>Posiciones abiertas</dt>
                    <dd>{portfolioSummary.posiciones_abiertas}</dd>
                  </div>
                </dl>
              </>
            ) : (
              <DashboardPanelState message="No hay resumen disponible para este portafolio." />
            )}
          </article>
        ) : null}

        {canReadSimulations ? (
          <article className="dashboard-panel">
            <header className="dashboard-panel__header">
              <div>
                <span className="dashboard-panel__eyebrow">Simulación</span>
                <h2>Ejecuciones</h2>
              </div>
            </header>

            {simulationsQuery.isPending ? (
              <DashboardPanelState message="Cargando simulaciones..." />
            ) : simulationsQuery.isError ? (
              <DashboardPanelState
                error
                message={simulationsQuery.error.message}
                onRetry={() => {
                  void simulationsQuery.refetch()
                }}
              />
            ) : simulationsQuery.data.items.length === 0 ? (
              <DashboardPanelState message="No hay ejecuciones de simulación disponibles." />
            ) : (
              <div className="dashboard-list">
                {simulationsQuery.data.items.map((execution) => (
                  <div className="dashboard-list__item" key={execution.id}>
                    <div>
                      <strong>{formatDashboardLabel(execution.estado)}</strong>
                      <span>Solicitada {formatDashboardDate(execution.fecha_solicitud)}</span>
                    </div>

                    <span className="dashboard-badge">
                      {formatDashboardPercentage(execution.porcentaje_progreso)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </article>
        ) : null}

        {canReadNotifications ? (
          <article className="dashboard-panel">
            <header className="dashboard-panel__header">
              <div>
                <span className="dashboard-panel__eyebrow">Notificaciones</span>
                <h2>Actividad disponible</h2>
              </div>
            </header>

            {notificationsQuery.isPending ? (
              <DashboardPanelState message="Cargando notificaciones..." />
            ) : notificationsQuery.isError ? (
              <DashboardPanelState
                error
                message={notificationsQuery.error.message}
                onRetry={() => {
                  void notificationsQuery.refetch()
                }}
              />
            ) : notificationsQuery.data.items.length === 0 ? (
              <DashboardPanelState message="No tienes notificaciones disponibles." />
            ) : (
              <div className="dashboard-list">
                {notificationsQuery.data.items.map((notification) => (
                  <div className="dashboard-list__item" key={notification.id}>
                    <div>
                      <strong>{notification.title}</strong>
                      <span>{notification.message}</span>
                      <span>{formatDashboardDate(notification.created_at)}</span>
                    </div>

                    <span className="dashboard-badge">
                      {formatDashboardLabel(notification.priority)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </article>
        ) : null}

        {canReadReports ? (
          <article className="dashboard-panel dashboard-panel--wide">
            <header className="dashboard-panel__header">
              <div>
                <span className="dashboard-panel__eyebrow">Inteligencia artificial</span>
                <h2>Recomendaciones</h2>
              </div>

              <Link className="dashboard-panel__link" to="/app/reports/recommendations">
                Ver reporte
              </Link>
            </header>

            {recommendationsQuery.isPending ? (
              <DashboardPanelState message="Cargando recomendaciones..." />
            ) : recommendationsQuery.isError ? (
              <DashboardPanelState
                error
                message={recommendationsQuery.error.message}
                onRetry={() => {
                  void recommendationsQuery.refetch()
                }}
              />
            ) : recommendationsQuery.data.items.length === 0 ? (
              <DashboardPanelState message="No hay recomendaciones disponibles." />
            ) : (
              <div className="dashboard-recommendations">
                {recommendationsQuery.data.items.map((recommendation) => (
                  <article
                    className="dashboard-recommendation"
                    key={recommendation.recommendation_id}
                  >
                    <div className="dashboard-recommendation__heading">
                      <div>
                        <span>{formatDashboardLabel(recommendation.type)}</span>
                        <h3>{recommendation.title ?? 'Recomendación'}</h3>
                      </div>

                      <span className="dashboard-badge">
                        {formatDashboardLabel(recommendation.risk_level)}
                      </span>
                    </div>

                    {recommendation.summary ? <p>{recommendation.summary}</p> : null}

                    {recommendation.asset_symbols && recommendation.asset_symbols.length > 0 ? (
                      <div className="dashboard-tags">
                        {recommendation.asset_symbols.map((symbol) => (
                          <span key={symbol}>{symbol}</span>
                        ))}
                      </div>
                    ) : null}

                    <span className="dashboard-recommendation__date">
                      {formatDashboardDate(recommendation.generated_at)}
                    </span>
                  </article>
                ))}
              </div>
            )}
          </article>
        ) : null}

        {canReadAssets ? (
          <article className="dashboard-panel dashboard-panel--wide">
            <header className="dashboard-panel__header">
              <div>
                <span className="dashboard-panel__eyebrow">Mercado</span>
                <h2>Activos disponibles</h2>
              </div>
            </header>

            {assetsQuery.isPending ? (
              <DashboardPanelState message="Cargando activos..." />
            ) : assetsQuery.isError ? (
              <DashboardPanelState
                error
                message={assetsQuery.error.message}
                onRetry={() => {
                  void assetsQuery.refetch()
                }}
              />
            ) : assetsQuery.data.items.length === 0 ? (
              <DashboardPanelState message="No hay activos disponibles." />
            ) : (
              <div className="dashboard-assets">
                {assetsQuery.data.items.map((asset) => (
                  <article className="dashboard-asset" key={asset.id}>
                    <div>
                      <strong>{asset.symbol}</strong>
                      <span>{asset.name}</span>
                    </div>

                    <dl>
                      <div>
                        <dt>Moneda</dt>
                        <dd>{asset.currency}</dd>
                      </div>

                      <div>
                        <dt>Estado</dt>
                        <dd>{formatDashboardLabel(asset.status)}</dd>
                      </div>
                    </dl>
                  </article>
                ))}
              </div>
            )}
          </article>
        ) : null}
      </div>
    </section>
  )
}
