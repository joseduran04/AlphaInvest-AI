import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type { PositionCreateRequest } from '@/api/types'
import { useAssets } from '@/features/market/hooks/useAssets'
import { useCreatePosition } from '@/features/portfolio/hooks/useCreatePosition'

interface CreatePositionFormProps {
  portfolioId: string
  onCancel: () => void
  onCreated: () => void
}

const createPositionSchema = z.object({
  activo_id: z.string().uuid('Selecciona un activo válido.'),
  cantidad: z
    .string()
    .trim()
    .min(1, 'Ingresa la cantidad.')
    .refine((value) => {
      const parsedValue = Number(value)

      return Number.isFinite(parsedValue) && parsedValue > 0
    }, 'La cantidad debe ser mayor que cero.'),
  precio_promedio_compra: z
    .string()
    .trim()
    .min(1, 'Ingresa el precio promedio.')
    .refine((value) => {
      const parsedValue = Number(value)

      return Number.isFinite(parsedValue) && parsedValue > 0
    }, 'El precio promedio debe ser mayor que cero.'),
  fecha_apertura: z.string(),
})

type CreatePositionFormValues = z.infer<typeof createPositionSchema>

function getCreatePositionErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      // El backend explica el conflicto: activo duplicado o moneda distinta
      // a la del portafolio.
      return error.message
    }

    if (error.status === 422) {
      return 'Los datos de la posición no son válidos. Revisa el formulario.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo agregar la posición. Inténtalo nuevamente.'
    }
  }

  return error.message
}

function toIsoDateTime(value: string): string | null {
  if (!value) {
    return null
  }

  const date = new Date(value)

  return Number.isNaN(date.getTime()) ? null : date.toISOString()
}

export function CreatePositionForm({ portfolioId, onCancel, onCreated }: CreatePositionFormProps) {
  const [assetSearch, setAssetSearch] = useState('')

  const assetsQuery = useAssets({
    search: assetSearch.trim() || undefined,
    status: 'ACTIVO',
  })

  const createPositionMutation = useCreatePosition(portfolioId)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreatePositionFormValues>({
    resolver: zodResolver(createPositionSchema),
    defaultValues: {
      activo_id: '',
      cantidad: '',
      precio_promedio_compra: '',
      fecha_apertura: '',
    },
  })

  async function submitPosition(values: CreatePositionFormValues) {
    if (createPositionMutation.isPending) {
      return
    }

    const fechaApertura = toIsoDateTime(values.fecha_apertura)

    const data: PositionCreateRequest = {
      activo_id: values.activo_id,
      cantidad: values.cantidad.trim(),
      precio_promedio_compra: values.precio_promedio_compra.trim(),
      fecha_apertura: fechaApertura,
    }

    try {
      await createPositionMutation.mutateAsync(data)
      onCreated()
    } catch {
      // React Query conserva el error en createPositionMutation.error.
    }
  }

  const assets = assetsQuery.data?.items ?? []

  return (
    <section className="portfolio-position-form" aria-labelledby="create-position-title">
      <header className="portfolio-position-form__header">
        <div>
          <p className="app__eyebrow">Nueva posición</p>
          <h3 id="create-position-title">Agregar posición</h3>
          <p>Registra una posición agregada para uno de los activos disponibles.</p>
        </div>
      </header>

      <form
        className="portfolio-position-form__form"
        onSubmit={(event) => {
          void handleSubmit(submitPosition)(event)
        }}
      >
        <div className="portfolio-position-form__grid">
          <label className="portfolio-field">
            <span>Buscar activo</span>
            <input
              type="search"
              value={assetSearch}
              placeholder="Símbolo o nombre"
              onChange={(event) => setAssetSearch(event.target.value)}
            />
          </label>

          <label className="portfolio-field">
            <span>Activo</span>
            <select {...register('activo_id')} disabled={assetsQuery.isPending}>
              <option value="">
                {assetsQuery.isPending ? 'Cargando activos...' : 'Selecciona un activo'}
              </option>

              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.symbol} — {asset.name} ({asset.currency})
                </option>
              ))}
            </select>

            {errors.activo_id ? (
              <small className="portfolio-field__error">{errors.activo_id.message}</small>
            ) : null}
          </label>

          <label className="portfolio-field">
            <span>Cantidad</span>
            <input type="number" min="0" step="any" inputMode="decimal" {...register('cantidad')} />
            {errors.cantidad ? (
              <small className="portfolio-field__error">{errors.cantidad.message}</small>
            ) : null}
          </label>

          <label className="portfolio-field">
            <span>Precio promedio de compra</span>
            <input
              type="number"
              min="0"
              step="any"
              inputMode="decimal"
              {...register('precio_promedio_compra')}
            />
            {errors.precio_promedio_compra ? (
              <small className="portfolio-field__error">
                {errors.precio_promedio_compra.message}
              </small>
            ) : null}
          </label>

          <label className="portfolio-field">
            <span>Fecha de apertura</span>
            <input type="datetime-local" {...register('fecha_apertura')} />
          </label>
        </div>

        {assetsQuery.isError ? (
          <div className="portfolio-position-form__error" role="alert">
            <strong>No fue posible consultar los activos.</strong>
            <span>{assetsQuery.error.message}</span>
          </div>
        ) : null}

        {createPositionMutation.isError ? (
          <div className="portfolio-position-form__error" role="alert">
            <strong>No fue posible agregar la posición.</strong>
            <span>{getCreatePositionErrorMessage(createPositionMutation.error)}</span>
          </div>
        ) : null}

        <div className="portfolio-position-form__actions">
          <button
            className="button button--secondary"
            type="button"
            disabled={createPositionMutation.isPending}
            onClick={onCancel}
          >
            Cancelar
          </button>

          <button
            className="button button--primary"
            type="submit"
            disabled={createPositionMutation.isPending}
          >
            {createPositionMutation.isPending ? 'Agregando posición...' : 'Agregar posición'}
          </button>
        </div>
      </form>
    </section>
  )
}
