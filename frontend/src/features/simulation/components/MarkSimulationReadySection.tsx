import { useState } from 'react'

import { ApiError } from '@/api/errors'
import type {
  SimulationConfigurationStatus,
  SimulationDistributionStatusResponse,
} from '@/api/types'
import { useMarkSimulationReady } from '@/features/simulation/hooks/useMarkSimulationReady'

interface MarkSimulationReadySectionProps {
  configurationId: string
  status: SimulationConfigurationStatus
  distribution: SimulationDistributionStatusResponse
  canUpdate: boolean
}

function getReadyErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 404) {
      return 'La configuración no existe o ya no está disponible.'
    }

    if (error.status === 409) {
      return 'La configuración no puede marcarse como lista. Verifica que siga en borrador y que la distribución sea válida.'
    }

    if (error.status === 422) {
      return 'El backend rechazó la solicitud para preparar la configuración.'
    }

    if (error.status >= 500) {
      return 'Ocurrió un problema en el servidor al preparar la simulación.'
    }
  }

  return error.message
}

export function MarkSimulationReadySection({
  configurationId,
  status,
  distribution,
  canUpdate,
}: MarkSimulationReadySectionProps) {
  const [confirmReady, setConfirmReady] = useState(false)

  const mutation = useMarkSimulationReady(configurationId)

  if (!canUpdate || status !== 'BORRADOR') {
    return null
  }

  const canMarkReady = distribution.distribucion_valida

  const handleReady = () => {
    mutation.mutate(undefined, {
      onSuccess: () => {
        setConfirmReady(false)
      },
    })
  }

  return (
    <section className="simulation-ready-section">
      <div className="simulation-ready-section__content">
        <div>
          <p className="simulation-results__eyebrow">Preparación</p>
          <h3>Preparar configuración</h3>
          <p>
            {canMarkReady
              ? 'La distribución es válida y la configuración puede marcarse como lista.'
              : 'Agrega al menos un activo y completa una distribución del 100 % para continuar.'}
          </p>
        </div>

        {!confirmReady ? (
          <button
            className="button button--primary"
            type="button"
            disabled={!canMarkReady || mutation.isPending}
            onClick={() => setConfirmReady(true)}
          >
            Marcar como lista
          </button>
        ) : null}
      </div>

      {confirmReady ? (
        <div className="simulation-ready-confirmation">
          <div>
            <strong>¿Marcar esta configuración como lista?</strong>
            <span>
              Después de continuar ya no podrás modificar sus parámetros ni los activos de la
              distribución.
            </span>
          </div>

          <div className="simulation-form__actions">
            <button
              className="button button--secondary"
              type="button"
              disabled={mutation.isPending}
              onClick={() => setConfirmReady(false)}
            >
              Cancelar
            </button>

            <button
              className="button button--primary"
              type="button"
              disabled={mutation.isPending}
              onClick={handleReady}
            >
              {mutation.isPending ? 'Preparando...' : 'Confirmar y marcar lista'}
            </button>
          </div>
        </div>
      ) : null}

      {mutation.isError ? (
        <p className="simulation-form__error">{getReadyErrorMessage(mutation.error)}</p>
      ) : null}
    </section>
  )
}
