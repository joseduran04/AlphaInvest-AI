import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useRiskProfileHistory } from '@/features/profile/hooks/useRiskProfileHistory'
import {
  formatRiskClassification,
  formatRiskConfidence,
  formatRiskDate,
  formatRiskScore,
} from '@/features/profile/utils/profileFormatters'

export function RiskProfileHistory() {
  const historyQuery = useRiskProfileHistory()

  if (historyQuery.isPending) {
    return <PageLoadingState message="Cargando historial de perfiles..." />
  }

  if (historyQuery.isError) {
    return (
      <PageErrorState
        title="No fue posible consultar tu historial"
        message={historyQuery.error.message}
        onRetry={() => {
          void historyQuery.refetch()
        }}
      />
    )
  }

  const history = historyQuery.data

  if (!history || history.items.length === 0) {
    return (
      <PageEmptyState
        title="Todavía no hay historial"
        description="Tus evaluaciones aparecerán aquí cuando generes perfiles de riesgo."
      />
    )
  }

  const profiles = [...history.items].sort((left, right) => {
    const leftTimestamp = new Date(left.started_at).getTime()
    const rightTimestamp = new Date(right.started_at).getTime()

    if (!Number.isFinite(leftTimestamp) || !Number.isFinite(rightTimestamp)) {
      return 0
    }

    return rightTimestamp - leftTimestamp
  })

  return (
    <section className="risk-history" aria-labelledby="risk-history-title">
      <header className="risk-history__header">
        <div>
          <p className="app__eyebrow">Historial</p>
          <h2 id="risk-history-title">Tus perfiles de riesgo</h2>
          <p>Consulta cómo ha cambiado tu clasificación a través de tus evaluaciones realizadas.</p>
        </div>

        <span className="risk-history__count">
          {history.total} {history.total === 1 ? 'evaluación' : 'evaluaciones'}
        </span>
      </header>

      <div className="risk-history__list">
        {profiles.map((profile) => (
          <article className="risk-history-item" key={profile.id}>
            <div className="risk-history-item__heading">
              <div>
                <span className="risk-history-item__label">Clasificación</span>
                <h3>{formatRiskClassification(profile.classification)}</h3>
              </div>

              <span
                className={
                  profile.current
                    ? 'risk-history-item__status risk-history-item__status--current'
                    : 'risk-history-item__status'
                }
              >
                {profile.current ? 'Vigente' : 'Finalizado'}
              </span>
            </div>

            <p className="risk-history-item__description">{profile.description}</p>

            <dl className="risk-history-item__details">
              <div>
                <dt>Puntuación</dt>
                <dd>{formatRiskScore(profile.score)}</dd>
              </div>

              <div>
                <dt>Confianza</dt>
                <dd>{formatRiskConfidence(profile.confidence)}</dd>
              </div>

              <div>
                <dt>Inicio</dt>
                <dd>{formatRiskDate(profile.started_at)}</dd>
              </div>

              <div>
                <dt>Fin</dt>
                <dd>
                  {profile.current ? 'Actualmente vigente' : formatRiskDate(profile.ended_at)}
                </dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  )
}
