import { useState } from 'react'

import { ApiError } from '@/api/errors'
import type { SimulationConfigurationStatus } from '@/api/types'
import { useArchiveSimulationConfiguration } from '@/features/simulation/hooks/useArchiveSimulationConfiguration'

interface ArchiveSimulationConfigurationSectionProps {
  configurationId: string
  status: SimulationConfigurationStatus
  canArchive: boolean
}

function getArchiveErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return 'La configuración no puede archivarse en su estado actual.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo archivar la configuración. Inténtalo nuevamente.'
    }
  }

  return error.message
}

export function ArchiveSimulationConfigurationSection({
  configurationId,
  status,
  canArchive,
}: ArchiveSimulationConfigurationSectionProps) {
  const [confirmArchive, setConfirmArchive] = useState(false)

  const archiveMutation = useArchiveSimulationConfiguration(configurationId)

  const isArchived = status === 'ARCHIVADA'
  const canSubmitArchive = canArchive && !isArchived

  async function handleArchive() {
    if (!canSubmitArchive || archiveMutation.isPending) {
      return
    }

    try {
      await archiveMutation.mutateAsync()
      setConfirmArchive(false)
    } catch {
      // React Query conserva el error en archiveMutation.error.
    }
  }

  if (!canArchive) {
    return null
  }

  return (
    <section className="simulation-detail-section simulation-archive">
      <header className="simulation-detail-section__header">
        <div>
          <p className="simulation-results__eyebrow">Administración</p>
          <h2>Archivado de configuración</h2>
        </div>
      </header>

      {isArchived ? (
        <div className="simulation-archive__message">
          <strong>Esta configuración ya está archivada.</strong>
          <span>No puede volver a ejecutarse la operación de archivado.</span>
        </div>
      ) : (
        <>
          <div className="simulation-archive__message">
            <strong>Archivar configuración</strong>
            <span>
              La configuración dejará de estar disponible para modificaciones posteriores. El
              backend validará nuevamente que la operación sea permitida.
            </span>
          </div>

          {!confirmArchive ? (
            <div className="simulation-archive__actions">
              <button
                className="button button--secondary"
                type="button"
                disabled={archiveMutation.isPending}
                onClick={() => setConfirmArchive(true)}
              >
                Archivar configuración
              </button>
            </div>
          ) : (
            <div className="simulation-archive__confirmation">
              <div>
                <strong>¿Confirmar archivado?</strong>
                <span>Esta operación cambiará el estado de la configuración.</span>
              </div>

              <div className="simulation-archive__actions">
                <button
                  className="button button--secondary"
                  type="button"
                  disabled={archiveMutation.isPending}
                  onClick={() => setConfirmArchive(false)}
                >
                  Cancelar
                </button>

                <button
                  className="button button--primary"
                  type="button"
                  disabled={archiveMutation.isPending}
                  onClick={() => {
                    void handleArchive()
                  }}
                >
                  {archiveMutation.isPending ? 'Archivando...' : 'Confirmar archivado'}
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {archiveMutation.isError ? (
        <div className="simulation-form__error" role="alert">
          <strong>No fue posible archivar la configuración.</strong>
          <span>{getArchiveErrorMessage(archiveMutation.error)}</span>
        </div>
      ) : null}

      {archiveMutation.isSuccess ? (
        <div className="simulation-archive__success" role="status">
          La configuración fue archivada correctamente.
        </div>
      ) : null}
    </section>
  )
}
