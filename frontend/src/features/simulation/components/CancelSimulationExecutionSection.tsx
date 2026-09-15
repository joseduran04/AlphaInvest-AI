import { useState } from 'react'

import { ApiError } from '@/api/errors'
import type { SimulationExecutionResponse } from '@/api/types'
import { useCancelSimulationExecution } from '@/features/simulation/hooks/useCancelSimulationExecution'

interface CancelSimulationExecutionSectionProps {
  execution: SimulationExecutionResponse
  canExecute: boolean
}

function getCancellationErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 404) {
      return 'La ejecución ya no está disponible.'
    }

    if (error.status === 409) {
      return 'La ejecución ya no puede cancelarse porque su estado cambió en el backend.'
    }

    if (error.status === 422) {
      return 'El backend rechazó la solicitud de cancelación.'
    }

    if (error.status >= 500) {
      return 'Ocurrió un problema en el servidor al cancelar la ejecución.'
    }
  }

  return error.message
}

export function CancelSimulationExecutionSection({
  execution,
  canExecute,
}: CancelSimulationExecutionSectionProps) {
  const [confirmCancellation, setConfirmCancellation] = useState(false)

  const cancelExecutionMutation = useCancelSimulationExecution(execution.id)

  const canCancel =
    canExecute && (execution.estado === 'PENDIENTE' || execution.estado === 'EJECUTANDO')

  if (!canCancel) {
    return null
  }

  const handleCancel = () => {
    cancelExecutionMutation.mutate(undefined, {
      onSuccess: () => {
        setConfirmCancellation(false)
      },
    })
  }

  return (
    <div className="simulation-execution-cancel">
      {!confirmCancellation ? (
        <button
          className="button button--secondary"
          type="button"
          disabled={cancelExecutionMutation.isPending}
          onClick={() => setConfirmCancellation(true)}
        >
          Cancelar ejecución
        </button>
      ) : (
        <div className="simulation-execution-cancel__confirmation">
          <div>
            <strong>¿Cancelar esta ejecución?</strong>
            <span>La ejecución dejará de estar activa. Esta acción no puede revertirse.</span>
          </div>

          <div className="simulation-form__actions">
            <button
              className="button button--secondary"
              type="button"
              disabled={cancelExecutionMutation.isPending}
              onClick={() => setConfirmCancellation(false)}
            >
              Volver
            </button>

            <button
              className="button button--primary"
              type="button"
              disabled={cancelExecutionMutation.isPending}
              onClick={handleCancel}
            >
              {cancelExecutionMutation.isPending ? 'Cancelando...' : 'Confirmar cancelación'}
            </button>
          </div>
        </div>
      )}

      {cancelExecutionMutation.isError ? (
        <p className="simulation-form__error">
          {getCancellationErrorMessage(cancelExecutionMutation.error)}
        </p>
      ) : null}
    </div>
  )
}
