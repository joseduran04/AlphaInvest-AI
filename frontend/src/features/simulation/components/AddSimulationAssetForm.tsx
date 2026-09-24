import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type { AssetResponse, SimulationConfigurationAssetCreateRequest } from '@/api/types'
import { useAddSimulationAsset } from '@/features/simulation/hooks/useAddSimulationAsset'

interface AddSimulationAssetFormProps {
  configurationId: string
  marketAssets: AssetResponse[]
  configuredAssetIds: Set<string>
  nextOrder: number
  isMarketLoading: boolean
  marketError: string | null
  onCancel: () => void
  onAdded: () => void
}

const addSimulationAssetSchema = z.object({
  activo_id: z.string().min(1, 'Selecciona un activo.'),
  porcentaje_asignado: z
    .string()
    .min(1, 'Ingresa el porcentaje asignado.')
    .refine((value) => {
      const parsedValue = Number(value)
      return Number.isFinite(parsedValue) && parsedValue > 0 && parsedValue <= 100
    }, 'El porcentaje debe ser mayor que 0 y menor o igual que 100.'),
  monto_inicial: z.string().refine((value) => {
    if (value.trim() === '') {
      return true
    }

    const parsedValue = Number(value)
    return Number.isFinite(parsedValue) && parsedValue >= 0
  }, 'El monto de referencia debe ser mayor o igual que cero.'),
  precio_inicial: z.string().refine((value) => {
    if (value.trim() === '') {
      return true
    }

    const parsedValue = Number(value)
    return Number.isFinite(parsedValue) && parsedValue >= 0
  }, 'El precio de referencia debe ser mayor o igual que cero.'),
  orden: z
    .string()
    .min(1, 'Ingresa el orden.')
    .refine((value) => {
      const parsedValue = Number(value)
      return Number.isInteger(parsedValue) && parsedValue > 0
    }, 'El orden debe ser un entero mayor que cero.'),
})

type AddSimulationAssetFormValues = z.infer<typeof addSimulationAssetSchema>

function getMutationErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return 'El activo o el orden seleccionado ya pertenece a la configuración.'
    }

    if (error.status === 422) {
      return 'El backend rechazó los datos del activo. Revisa los valores ingresados.'
    }

    if (error.status >= 500) {
      return 'Ocurrió un problema en el servidor al agregar el activo.'
    }
  }

  return error.message
}

export function AddSimulationAssetForm({
  configurationId,
  marketAssets,
  configuredAssetIds,
  nextOrder,
  isMarketLoading,
  marketError,
  onCancel,
  onAdded,
}: AddSimulationAssetFormProps) {
  const mutation = useAddSimulationAsset(configurationId)

  const availableAssets = marketAssets.filter((asset) => !configuredAssetIds.has(asset.id))

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AddSimulationAssetFormValues>({
    resolver: zodResolver(addSimulationAssetSchema),
    defaultValues: {
      activo_id: '',
      porcentaje_asignado: '',
      monto_inicial: '',
      precio_inicial: '',
      orden: String(nextOrder),
    },
  })

  const handleValidSubmit = (values: AddSimulationAssetFormValues) => {
    const data: SimulationConfigurationAssetCreateRequest = {
      activo_id: values.activo_id,
      porcentaje_asignado: values.porcentaje_asignado.trim(),
      orden: Number(values.orden),
    }

    if (values.monto_inicial.trim() !== '') {
      data.monto_inicial = values.monto_inicial.trim()
    }

    if (values.precio_inicial.trim() !== '') {
      data.precio_inicial = values.precio_inicial.trim()
    }

    mutation.mutate(data, {
      onSuccess: onAdded,
    })
  }

  return (
    <section className="simulation-asset-form">
      <header>
        <p className="simulation-results__eyebrow">Nuevo activo</p>
        <h3>Agregar activo a la simulación</h3>
      </header>

      <form onSubmit={handleSubmit(handleValidSubmit)}>
        <div className="simulation-asset-form__grid">
          <label className="form-field simulation-asset-form__wide">
            <span>Activo</span>
            <select {...register('activo_id')} disabled={mutation.isPending || isMarketLoading}>
              <option value="">Selecciona un activo</option>

              {availableAssets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.symbol} — {asset.name} ({asset.currency})
                </option>
              ))}
            </select>
            {errors.activo_id ? <small>{errors.activo_id.message}</small> : null}
          </label>

          <label className="form-field">
            <span>Porcentaje asignado</span>
            <input
              {...register('porcentaje_asignado')}
              type="number"
              min="0.00000001"
              max="100"
              step="0.00000001"
              disabled={mutation.isPending}
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
              disabled={mutation.isPending}
            />
            {errors.orden ? <small>{errors.orden.message}</small> : null}
          </label>

          <label className="form-field">
            <span>Monto de referencia (opcional)</span>
            <input
              {...register('monto_inicial')}
              type="number"
              min="0"
              step="0.00000001"
              disabled={mutation.isPending}
            />
            {errors.monto_inicial ? <small>{errors.monto_inicial.message}</small> : null}
            <span className="metric-hint">
              Dato informativo: no cambia el cálculo. La simulación asigna capital inicial ×
              porcentaje.
            </span>
          </label>

          <label className="form-field">
            <span>Precio de referencia (opcional)</span>
            <input
              {...register('precio_inicial')}
              type="number"
              min="0"
              step="0.00000001"
              disabled={mutation.isPending}
            />
            {errors.precio_inicial ? <small>{errors.precio_inicial.message}</small> : null}
            <span className="metric-hint">
              Dato informativo: la simulación usa el precio histórico de la fecha de inicio
              efectiva.
            </span>
          </label>
        </div>

        {marketError ? (
          <p className="simulation-form__error">
            No fue posible cargar el catálogo de activos: {marketError}
          </p>
        ) : null}

        {!isMarketLoading && !marketError && availableAssets.length === 0 ? (
          <p className="simulation-form__notice">No hay activos disponibles para agregar.</p>
        ) : null}

        {mutation.isError ? (
          <p className="simulation-form__error">{getMutationErrorMessage(mutation.error)}</p>
        ) : null}

        <div className="simulation-form__actions">
          <button
            className="button button--secondary"
            type="button"
            disabled={mutation.isPending}
            onClick={onCancel}
          >
            Cancelar
          </button>

          <button
            className="button button--primary"
            type="submit"
            disabled={
              mutation.isPending ||
              isMarketLoading ||
              marketError !== null ||
              availableAssets.length === 0
            }
          >
            {mutation.isPending ? 'Agregando...' : 'Agregar activo'}
          </button>
        </div>
      </form>
    </section>
  )
}
