import { useState } from 'react'

import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { RiskProfileHistory } from '@/features/profile/components/RiskProfileHistory'
import { RiskQuestionnaire } from '@/features/profile/components/RiskQuestionnaire'
import { useCurrentRiskProfile } from '@/features/profile/hooks/useCurrentRiskProfile'
import {
  formatRiskClassification,
  formatRiskConfidence,
  formatRiskDate,
  formatRiskScore,
} from '@/features/profile/utils/profileFormatters'

export function RiskProfilePage() {
  const currentProfileQuery = useCurrentRiskProfile()
  const [isEvaluating, setIsEvaluating] = useState(false)

  if (currentProfileQuery.isPending) {
    return <PageLoadingState message="Cargando tu perfil de riesgo..." />
  }

  if (currentProfileQuery.isError) {
    return (
      <PageErrorState
        title="No fue posible consultar tu perfil de riesgo"
        message={currentProfileQuery.error.message}
        onRetry={() => {
          void currentProfileQuery.refetch()
        }}
      />
    )
  }

  if (isEvaluating) {
    return (
      <RiskQuestionnaire
        onCancel={() => {
          setIsEvaluating(false)
        }}
        onCompleted={() => {
          setIsEvaluating(false)
        }}
      />
    )
  }

  if (currentProfileQuery.data === null) {
    return (
      <section className="risk-profile-page">
        <header className="risk-profile-page__header">
          <p className="app__eyebrow">Perfil de riesgo</p>
          <h1>Conoce tu perfil como inversionista</h1>
          <p className="app__description">
            Responde el cuestionario para identificar tu tolerancia al riesgo y establecer un perfil
            que AlphaInvest AI podrá utilizar como referencia en sus herramientas de análisis.
          </p>
        </header>

        <PageEmptyState
          title="Todavía no tienes un perfil de riesgo"
          description="Completa una evaluación para obtener tu clasificación de riesgo."
          action={
            <button
              className="button button--primary"
              type="button"
              onClick={() => {
                setIsEvaluating(true)
              }}
            >
              Comenzar evaluación
            </button>
          }
        />
      </section>
    )
  }

  const profile = currentProfileQuery.data

  return (
    <section className="risk-profile-page">
      <header className="risk-profile-page__header">
        <p className="app__eyebrow">Perfil de riesgo</p>
        <h1>Tu perfil actual</h1>
        <p className="app__description">
          Esta clasificación representa tu perfil de riesgo vigente en AlphaInvest AI.
        </p>
      </header>

      <article className="risk-profile-card">
        <div className="risk-profile-card__heading">
          <div>
            <span className="risk-profile-card__label">Clasificación</span>
            <h2>{formatRiskClassification(profile.classification)}</h2>
          </div>

          {profile.current ? <span className="risk-profile-card__status">Vigente</span> : null}
        </div>

        <p className="risk-profile-card__description">{profile.description}</p>

        <dl className="risk-profile-card__details">
          <div>
            <dt>Puntuación</dt>
            <dd>{formatRiskScore(profile.score)}</dd>
          </div>

          <div>
            <dt>Confianza</dt>
            <dd>{formatRiskConfidence(profile.confidence)}</dd>
          </div>

          <div>
            <dt>Vigente desde</dt>
            <dd>{formatRiskDate(profile.started_at)}</dd>
          </div>
        </dl>

        <div className="risk-profile-card__actions">
          <button
            className="button button--primary"
            type="button"
            onClick={() => {
              setIsEvaluating(true)
            }}
          >
            Volver a evaluar
          </button>
        </div>
      </article>

      <RiskProfileHistory />
    </section>
  )
}
