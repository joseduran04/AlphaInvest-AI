import { useState } from 'react'

import type { AssetResponse, PositionResponse } from '@/api/types'
import { EditPositionForm } from '@/features/portfolio/components/EditPositionForm'
import { useDeletePosition } from '@/features/portfolio/hooks/useDeletePosition'
import { formatCurrency } from '@/lib/formatters'

interface PositionCardProps {
  portfolioId: string
  position: PositionResponse
  asset?: AssetResponse
  canUpdate: boolean
}

function formatPercentage(value: string | null): string {
  if (value === null) {
    return 'No disponible'
  }

  const parsedValue = Number(value)

  return Number.isFinite(parsedValue) ? `${parsedValue.toFixed(2)} %` : value
}

function formatQuantity(value: string): string {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return new Intl.NumberFormat('es-MX', {
    maximumFractionDigits: 8,
  }).format(parsedValue)
}

export function PositionCard({ portfolioId, position, asset, canUpdate }: PositionCardProps) {
  const [editing, setEditing] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const deletePositionMutation = useDeletePosition(portfolioId, position.id)

  async function handleDelete() {
    if (deletePositionMutation.isPending) {
      return
    }

    try {
      await deletePositionMutation.mutateAsync()
      setConfirmDelete(false)
    } catch {
      // React Query conserva el error en deletePositionMutation.error.
    }
  }

  return (
    <article className="portfolio-position-card">
      <header className="portfolio-position-card__header">
        <div>
          <strong>{asset ? asset.symbol : 'Activo'}</strong>
          <span>{asset?.name ?? position.activo_id}</span>
        </div>

        <span className="portfolio-position-status">{position.estado}</span>
      </header>

      {editing ? (
        <EditPositionForm
          portfolioId={portfolioId}
          position={position}
          onCancel={() => setEditing(false)}
          onUpdated={() => setEditing(false)}
        />
      ) : (
        <>
          <dl className="portfolio-position-card__metrics">
            <div>
              <dt>Cantidad</dt>
              <dd>{formatQuantity(position.cantidad)}</dd>
            </div>

            <div>
              <dt>Precio promedio</dt>
              <dd>{formatCurrency(position.precio_promedio_compra, position.moneda)}</dd>
            </div>

            <div>
              <dt>Costo total</dt>
              <dd>{formatCurrency(position.costo_total, position.moneda)}</dd>
            </div>

            <div>
              <dt>Precio actual</dt>
              <dd>
                {position.precio_actual === null
                  ? 'No disponible'
                  : formatCurrency(position.precio_actual, position.moneda)}
              </dd>
            </div>

            <div>
              <dt>Valor actual</dt>
              <dd>
                {position.valor_actual === null
                  ? 'No disponible'
                  : formatCurrency(position.valor_actual, position.moneda)}
              </dd>
            </div>

            <div>
              <dt>Ganancia / pérdida</dt>
              <dd>
                {position.ganancia_perdida === null
                  ? 'No disponible'
                  : formatCurrency(position.ganancia_perdida, position.moneda)}
              </dd>
            </div>

            <div>
              <dt>Rendimiento</dt>
              <dd>{formatPercentage(position.rendimiento_porcentaje)}</dd>
            </div>

            <div>
              <dt>Moneda</dt>
              <dd>{position.moneda}</dd>
            </div>
          </dl>

          {canUpdate ? (
            <div className="portfolio-position-card__actions">
              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  setConfirmDelete(false)
                  setEditing(true)
                }}
              >
                Editar posición
              </button>

              {!confirmDelete ? (
                <button
                  className="button button--secondary"
                  type="button"
                  onClick={() => setConfirmDelete(true)}
                >
                  Eliminar posición
                </button>
              ) : (
                <div className="portfolio-position-card__confirm">
                  <span>¿Eliminar esta posición?</span>

                  <button
                    className="button button--secondary"
                    type="button"
                    disabled={deletePositionMutation.isPending}
                    onClick={() => setConfirmDelete(false)}
                  >
                    Cancelar
                  </button>

                  <button
                    className="button button--primary"
                    type="button"
                    disabled={deletePositionMutation.isPending}
                    onClick={() => {
                      void handleDelete()
                    }}
                  >
                    {deletePositionMutation.isPending ? 'Eliminando...' : 'Confirmar'}
                  </button>
                </div>
              )}
            </div>
          ) : null}

          {deletePositionMutation.isError ? (
            <div className="portfolio-position-form__error" role="alert">
              <strong>No fue posible eliminar la posición.</strong>
              <span>{deletePositionMutation.error.message}</span>
            </div>
          ) : null}
        </>
      )}
    </article>
  )
}
