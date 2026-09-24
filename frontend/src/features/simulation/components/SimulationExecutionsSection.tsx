import { useState } from 'react'

import { ApiError } from '@/api/errors'
import type {
  SimulationConfigurationStatus,
  SimulationExecutionResponse,
  SimulationExecutionStatus,
} from '@/api/types'
import { CancelSimulationExecutionSection } from '@/features/simulation/components/CancelSimulationExecutionSection'
import { useCreateSimulationExecution } from '@/features/simulation/hooks/useCreateSimulationExecution'
import { useSimulationExecutions } from '@/features/simulation/hooks/useSimulationExecutions'
import { SimulationResultSection } from '@/features/simulation/components/SimulationResultSection'

interface SimulationExecutionsSectionProps {
  configurationId: string
  configurationStatus: SimulationConfigurationStatus
  canRead: boolean
  canExecute: boolean
  requestedStartDate?: string | null
  requestedEndDate?: string | null
}

function formatExecutionStatus(status: SimulationExecutionStatus): string {
  switch (status) {
    case 'PENDIENTE':
      return 'Pendiente'
    case 'EJECUTANDO':
      return 'Ejecutando'
    case 'COMPLETADA':
      return 'Completada'
    case 'FALLIDA':
      return 'Fallida'
    case 'CANCELADA':
      return 'Cancelada'
  }
}

function formatDateTime(value: string | null): string {
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

function formatProgress(value: string): string {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}

function getCreateExecutionErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 404) {
      return 'La configuración o una versión de modelo asociada no está disponible.'
    }

    if (error.status === 409) {
      return 'No fue posible iniciar la ejecución. Verifica que la configuración siga lista, que su distribución sea válida y que no exista otra ejecución activa.'
    }

    if (error.status === 422) {
      return 'El backend rechazó los datos de la solicitud de ejecución.'
    }

    if (error.status >= 500) {
      return 'Ocurrió un problema en el servidor al solicitar la ejecución.'
    }
  }

  return error.message
}

function SimulationExecutionItem({
  execution,
  canExecute,
  requestedStartDate,
  requestedEndDate,
}: {
  execution: SimulationExecutionResponse
  canExecute: boolean
  requestedStartDate?: string | null
  requestedEndDate?: string | null
}) {
  const [showResult, setShowResult] = useState(false)

  return (
    <article className="simulation-execution-card">
      <div className="simulation-execution-card__header">
        <div>
          <span className="simulation-execution-card__label">Ejecución</span>
          <strong>{execution.id}</strong>
        </div>

        <span
          className={`simulation-execution-status simulation-execution-status--${execution.estado.toLowerCase()}`}
        >
          {formatExecutionStatus(execution.estado)}
        </span>
      </div>

      <dl className="simulation-execution-grid">
        <div>
          <dt>Progreso</dt>
          <dd>{formatProgress(execution.porcentaje_progreso)}</dd>
        </div>

        <div>
          <dt>Solicitada</dt>
          <dd>{formatDateTime(execution.fecha_solicitud)}</dd>
        </div>

        <div>
          <dt>Inicio</dt>
          <dd>{formatDateTime(execution.fecha_inicio)}</dd>
        </div>

        <div>
          <dt>Fin</dt>
          <dd>{formatDateTime(execution.fecha_fin)}</dd>
        </div>
      </dl>

      {execution.mensaje_error ? (
        <div className="simulation-execution-card__error">
          <strong>Error de ejecución</strong>
          <span>{execution.mensaje_error}</span>
        </div>
      ) : null}

      {execution.estado === 'COMPLETADA' ? (
        <div className="simulation-execution-result">
          {!showResult ? (
            <button
              className="button button--secondary"
              type="button"
              onClick={() => setShowResult(true)}
            >
              Ver resultados
            </button>
          ) : (
            <SimulationResultSection
              executionId={execution.id}
              onClose={() => setShowResult(false)}
              requestedStartDate={requestedStartDate}
              requestedEndDate={requestedEndDate}
            />
          )}
        </div>
      ) : null}

      <CancelSimulationExecutionSection execution={execution} canExecute={canExecute} />
    </article>
  )
}

export function SimulationExecutionsSection({
  configurationId,
  configurationStatus,
  canRead,
  canExecute,
  requestedStartDate,
  requestedEndDate,
}: SimulationExecutionsSectionProps) {
  const [confirmExecution, setConfirmExecution] = useState(false)

  const executionsQuery = useSimulationExecutions(
    {
      configuracion_id: configurationId,
      limit: 50,
      offset: 0,
    },
    canRead,
  )

  const createExecutionMutation = useCreateSimulationExecution()

  if (!canRead) {
    return null
  }

  const executions = executionsQuery.data?.items ?? []

  const hasActiveExecution = executions.some(
    (execution) => execution.estado === 'PENDIENTE' || execution.estado === 'EJECUTANDO',
  )

  const canCreateExecution = canExecute && configurationStatus === 'LISTA' && !hasActiveExecution

  const handleCreateExecution = () => {
    createExecutionMutation.mutate(
      {
        configuracion_id: configurationId,
      },
      {
        onSuccess: () => {
          setConfirmExecution(false)
        },
      },
    )
  }

  return (
    <section className="simulation-detail-section">
      <header className="simulation-detail-section__header">
        <div>
          <p className="simulation-results__eyebrow">Ejecución</p>
          <h2>Ejecuciones de la simulación</h2>
          <p>
            Consulta las solicitudes realizadas para esta configuración e inicia una nueva ejecución
            cuando esté disponible.
          </p>
        </div>

        {canExecute && configurationStatus === 'LISTA' && !confirmExecution ? (
          <button
            className="button button--primary"
            type="button"
            disabled={
              executionsQuery.isPending || hasActiveExecution || createExecutionMutation.isPending
            }
            onClick={() => setConfirmExecution(true)}
          >
            {hasActiveExecution ? 'Ejecución activa' : 'Ejecutar simulación'}
          </button>
        ) : null}
      </header>

      {hasActiveExecution ? (
        <div className="simulation-execution-tracking" role="status">
          <span className="simulation-execution-tracking__indicator" />
          <span>
            La ejecución está siendo seguida automáticamente. Su estado se actualizará sin recargar
            la página.
          </span>
        </div>
      ) : null}

      {confirmExecution ? (
        <div className="simulation-execution-confirmation">
          <div>
            <strong>¿Solicitar la ejecución de esta simulación?</strong>
            <span>
              La ejecución será procesada por el backend utilizando la configuración actualmente
              lista.
            </span>
          </div>

          <div className="simulation-form__actions">
            <button
              className="button button--secondary"
              type="button"
              disabled={createExecutionMutation.isPending}
              onClick={() => setConfirmExecution(false)}
            >
              Cancelar
            </button>

            <button
              className="button button--primary"
              type="button"
              disabled={!canCreateExecution || createExecutionMutation.isPending}
              onClick={handleCreateExecution}
            >
              {createExecutionMutation.isPending ? 'Solicitando...' : 'Confirmar ejecución'}
            </button>
          </div>
        </div>
      ) : null}

      {createExecutionMutation.isError ? (
        <p className="simulation-form__error">
          {getCreateExecutionErrorMessage(createExecutionMutation.error)}
        </p>
      ) : null}

      {executionsQuery.isPending ? (
        <div className="simulation-execution-state">
          <span>Cargando ejecuciones...</span>
        </div>
      ) : null}

      {executionsQuery.isError ? (
        <div className="simulation-execution-state simulation-execution-state--error">
          <span>{executionsQuery.error.message}</span>
          <button
            className="button button--secondary"
            type="button"
            onClick={() => {
              void executionsQuery.refetch()
            }}
          >
            Reintentar
          </button>
        </div>
      ) : null}

      {executionsQuery.isSuccess && executions.length === 0 ? (
        <div className="simulation-execution-state">
          <span>Todavía no existen ejecuciones para esta configuración.</span>
        </div>
      ) : null}

      {executionsQuery.isSuccess && executions.length > 0 ? (
        <div className="simulation-executions-list">
          {executions.map((execution) => (
            <SimulationExecutionItem
              key={execution.id}
              execution={execution}
              canExecute={canExecute}
              requestedStartDate={requestedStartDate}
              requestedEndDate={requestedEndDate}
            />
          ))}
        </div>
      ) : null}
    </section>
  )
}
