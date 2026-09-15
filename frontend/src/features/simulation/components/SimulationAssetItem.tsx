import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type {
  AssetResponse,
  SimulationConfigurationAssetResponse,
  SimulationConfigurationAssetUpdateRequest,
} from '@/api/types'
import { useDeleteSimulationAsset } from '@/features/simulation/hooks/useDeleteSimulationAsset'
import { useUpdateSimulationAsset } from '@/features/simulation/hooks/useUpdateSimulationAsset'
import { formatCurrency } from '@/lib/formatters'

interface SimulationAssetItemProps {
  configurationId: string
  configuredAsset: SimulationConfigurationAssetResponse
  marketAsset?: AssetResponse
  currency: string
  canManage: boolean
}

const editAssetSchema = z.object({
  porcentaje_asignado: z.string().refine((value) => {
    const parsedValue = Number(value)
    return Number.isFinite(parsedValue) && parsedValue > 0 && parsedValue <= 100
  }, 'El porcentaje debe ser mayor que 0 y menor o igual que 100.'),
  monto_inicial: z.string().refine((value) => {
    if (value.trim() === '') {
      return true
    }

    const parsedValue = Number(value)
    return Number.isFinite(parsedValue) && parsedValue >= 0
  }, 'El monto inicial debe ser mayor o igual que cero.'),
  precio_inicial: z.string().refine((value) => {
    if (value.trim() === '') {
      return true
    }

    const parsedValue = Number(value)
    return Number.isFinite(parsedValue) && parsedValue >= 0
  }, 'El precio inicial debe ser mayor o igual que cero.'),
  orden: z.string().refine((value) => {
    const parsedValue = Number(value)
    return Number.isInteger(parsedValue) && parsedValue > 0
  }, 'El orden debe ser un entero mayor que cero.'),
})

type EditAssetFormValues = z.infer<typeof editAssetSchema>

function formatPercentage(value: string): string {
  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}

function getMutationErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return 'El orden seleccionado ya está ocupado por otro activo.'
    }

    if (error.status === 422) {
      return 'El backend rechazó los datos enviados. Revisa los valores.'
    }

    if (error.status >= 500) {
      return 'Ocurrió un problema en el servidor al modificar el activo.'
    }
  }

  return error.message
}

export function SimulationAssetItem({
  configurationId,
  configuredAsset,
  marketAsset,
  currency,
  canManage,
}: SimulationAssetItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const updateMutation = useUpdateSimulationAsset(configurationId, configuredAsset.activo_id)
  const deleteMutation = useDeleteSimulationAsset(configurationId, configuredAsset.activo_id)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<EditAssetFormValues>({
    resolver: zodResolver(editAssetSchema),
    defaultValues: {
      porcentaje_asignado: configuredAsset.porcentaje_asignado,
      monto_inicial: configuredAsset.monto_inicial ?? '',
      precio_inicial: configuredAsset.precio_inicial ?? '',
      orden: String(configuredAsset.orden),
    },
  })

  const handleCancelEdit = () => {
    reset({
      porcentaje_asignado: configuredAsset.porcentaje_asignado,
      monto_inicial: configuredAsset.monto_inicial ?? '',
      precio_inicial: configuredAsset.precio_inicial ?? '',
      orden: String(configuredAsset.orden),
    })
    setIsEditing(false)
  }

  const handleValidSubmit = (values: EditAssetFormValues) => {
    const data: SimulationConfigurationAssetUpdateRequest = {
      porcentaje_asignado: values.porcentaje_asignado.trim(),
      monto_inicial: values.monto_inicial.trim() === '' ? null : values.monto_inicial.trim(),
      precio_inicial: values.precio_inicial.trim() === '' ? null : values.precio_inicial.trim(),
      orden: Number(values.orden),
    }

    updateMutation.mutate(data, {
      onSuccess: () => {
        setIsEditing(false)
      },
    })
  }

  const handleDelete = () => {
    deleteMutation.mutate(undefined, {
      onSuccess: () => {
        setConfirmDelete(false)
      },
    })
  }

  const assetTitle = marketAsset
    ? `${marketAsset.symbol} · ${marketAsset.name}`
    : configuredAsset.activo_id

  return (
    <article className="simulation-asset-item">
      <header className="simulation-asset-item__header">
        <div>
          <strong>{assetTitle}</strong>
          <span>
            {marketAsset
              ? `${marketAsset.asset_type.name} · ${marketAsset.market.name}`
              : 'Información de mercado no disponible'}
          </span>
        </div>

        <span className="simulation-asset-item__percentage">
          {formatPercentage(configuredAsset.porcentaje_asignado)}
        </span>
      </header>

      {isEditing && canManage ? (
        <form className="simulation-asset-edit-form" onSubmit={handleSubmit(handleValidSubmit)}>
          <div className="simulation-asset-form__grid">
            <label className="form-field">
              <span>Porcentaje asignado</span>
              <input
                {...register('porcentaje_asignado')}
                type="number"
                min="0.00000001"
                max="100"
                step="0.00000001"
                disabled={updateMutation.isPending}
              />
              {errors.porcentaje_asignado ? (
                <small>{errors.porcentaje_asignado.message}</small>
              ) : null}
            </label>

            <label className="form-field">
              <span>Orden</span>
              <input
                {...register('orden')}
                type="number"
                min="1"
                step="1"
                disabled={updateMutation.isPending}
              />
              {errors.orden ? <small>{errors.orden.message}</small> : null}
            </label>

            <label className="form-field">
              <span>Monto inicial</span>
              <input
                {...register('monto_inicial')}
                type="number"
                min="0"
                step="0.00000001"
                disabled={updateMutation.isPending}
              />
              {errors.monto_inicial ? <small>{errors.monto_inicial.message}</small> : null}
            </label>

            <label className="form-field">
              <span>Precio inicial</span>
              <input
                {...register('precio_inicial')}
                type="number"
                min="0"
                step="0.00000001"
                disabled={updateMutation.isPending}
              />
              {errors.precio_inicial ? <small>{errors.precio_inicial.message}</small> : null}
            </label>
          </div>

          {updateMutation.isError ? (
            <p className="simulation-form__error">
              {getMutationErrorMessage(updateMutation.error)}
            </p>
          ) : null}

          <div className="simulation-form__actions">
            <button
              className="button button--secondary"
              type="button"
              disabled={updateMutation.isPending}
              onClick={handleCancelEdit}
            >
              Cancelar
            </button>

            <button
              className="button button--primary"
              type="submit"
              disabled={updateMutation.isPending || !isDirty}
            >
              {updateMutation.isPending ? 'Guardando...' : 'Guardar cambios'}
            </button>
          </div>
        </form>
      ) : (
        <>
          <dl className="simulation-asset-item__details">
            <div>
              <dt>Monto inicial</dt>
              <dd>
                {configuredAsset.monto_inicial === null
                  ? 'No configurado'
                  : formatCurrency(configuredAsset.monto_inicial, currency)}
              </dd>
            </div>

            <div>
              <dt>Precio inicial</dt>
              <dd>
                {configuredAsset.precio_inicial === null
                  ? 'No configurado'
                  : formatCurrency(
                      configuredAsset.precio_inicial,
                      marketAsset?.currency ?? currency,
                    )}
              </dd>
            </div>

            <div>
              <dt>Orden</dt>
              <dd>{configuredAsset.orden}</dd>
            </div>
          </dl>

          {canManage ? (
            <div className="simulation-asset-item__actions">
              {!confirmDelete ? (
                <>
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => setIsEditing(true)}
                  >
                    Editar
                  </button>

                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => setConfirmDelete(true)}
                  >
                    Eliminar
                  </button>
                </>
              ) : (
                <div className="simulation-asset-delete-confirmation">
                  <div>
                    <strong>¿Eliminar este activo?</strong>
                    <span>El backend recalculará la distribución de la configuración.</span>
                  </div>

                  <div className="simulation-form__actions">
                    <button
                      className="button button--secondary"
                      type="button"
                      disabled={deleteMutation.isPending}
                      onClick={() => setConfirmDelete(false)}
                    >
                      Cancelar
                    </button>

                    <button
                      className="button button--primary"
                      type="button"
                      disabled={deleteMutation.isPending}
                      onClick={handleDelete}
                    >
                      {deleteMutation.isPending ? 'Eliminando...' : 'Confirmar eliminación'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </>
      )}

      {deleteMutation.isError ? (
        <p className="simulation-form__error">{getMutationErrorMessage(deleteMutation.error)}</p>
      ) : null}
    </article>
  )
}
