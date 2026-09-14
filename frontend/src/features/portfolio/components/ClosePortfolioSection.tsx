import { useState } from 'react'

import { ApiError } from '@/api/errors'
import type { PortfolioStatus } from '@/api/types'
import { useClosePortfolio } from '@/features/portfolio/hooks/useClosePortfolio'

interface ClosePortfolioSectionProps {
  portfolioId: string
  status: PortfolioStatus
  openPositions: number
  canClose: boolean
}

function getCloseErrorMessage(error: Error): string {
  if (error instanceof ApiError && error.status === 409) {
    return 'El portafolio no puede cerrarse mientras existan posiciones abiertas.'
  }

  return error.message
}

export function ClosePortfolioSection({
  portfolioId,
  status,
  openPositions,
  canClose,
}: ClosePortfolioSectionProps) {
  const [confirmClose, setConfirmClose] = useState(false)

  const closePortfolioMutation = useClosePortfolio(portfolioId)

  const isActive = status === 'ACTIVO'
  const hasOpenPositions = openPositions > 0
  const canSubmitClose = canClose && isActive && !hasOpenPositions

  async function handleClose() {
    if (!canSubmitClose || closePortfolioMutation.isPending) {
      return
    }

    try {
      await closePortfolioMutation.mutateAsync()
      setConfirmClose(false)
    } catch {
      // React Query conserva el error en closePortfolioMutation.error.
    }
  }

  if (!canClose) {
    return null
  }

  return (
    <section className="portfolio-detail-section portfolio-close">
      <header className="portfolio-detail-section__header">
        <div>
          <p className="portfolio-results__eyebrow">Administración</p>
          <h2>Cierre del portafolio</h2>
        </div>
      </header>

      {!isActive ? (
        <div className="portfolio-close__message">
          <strong>Este portafolio ya no está activo.</strong>
          <span>
            Su estado actual es {status.toLowerCase()} y no puede volver a ejecutarse la operación
            de cierre.
          </span>
        </div>
      ) : hasOpenPositions ? (
        <div className="portfolio-close__message">
          <strong>No es posible cerrar el portafolio todavía.</strong>
          <span>
            Existen {openPositions} posiciones abiertas. Elimina las posiciones abiertas antes de
            solicitar el cierre.
          </span>
        </div>
      ) : (
        <>
          <div className="portfolio-close__message">
            <strong>El portafolio está listo para cerrarse.</strong>
            <span>
              El cierre cambiará su estado actual y registrará la fecha de cierre. Esta acción debe
              confirmarse explícitamente.
            </span>
          </div>

          {!confirmClose ? (
            <div className="portfolio-close__actions">
              <button
                className="button button--secondary"
                type="button"
                disabled={closePortfolioMutation.isPending}
                onClick={() => setConfirmClose(true)}
              >
                Cerrar portafolio
              </button>
            </div>
          ) : (
            <div className="portfolio-close__confirmation">
              <div>
                <strong>¿Confirmar cierre del portafolio?</strong>
                <span>El backend validará nuevamente que el cierre sea permitido.</span>
              </div>

              <div className="portfolio-close__actions">
                <button
                  className="button button--secondary"
                  type="button"
                  disabled={closePortfolioMutation.isPending}
                  onClick={() => setConfirmClose(false)}
                >
                  Cancelar
                </button>

                <button
                  className="button button--primary"
                  type="button"
                  disabled={closePortfolioMutation.isPending}
                  onClick={() => {
                    void handleClose()
                  }}
                >
                  {closePortfolioMutation.isPending ? 'Cerrando...' : 'Confirmar cierre'}
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {closePortfolioMutation.isError ? (
        <div className="portfolio-position-form__error" role="alert">
          <strong>No fue posible cerrar el portafolio.</strong>
          <span>{getCloseErrorMessage(closePortfolioMutation.error)}</span>
        </div>
      ) : null}

      {closePortfolioMutation.isSuccess ? (
        <div className="portfolio-close__success" role="status">
          El portafolio fue cerrado correctamente.
        </div>
      ) : null}
    </section>
  )
}
