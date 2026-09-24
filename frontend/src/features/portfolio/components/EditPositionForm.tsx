import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type { PositionResponse, PositionUpdateRequest } from '@/api/types'
import { useUpdatePosition } from '@/features/portfolio/hooks/useUpdatePosition'

interface EditPositionFormProps {
  portfolioId: string
  position: PositionResponse
  onCancel: () => void
  onUpdated: () => void
}

const editPositionSchema = z.object({
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
})

type EditPositionFormValues = z.infer<typeof editPositionSchema>

function getUpdatePositionErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      // Por ejemplo, efectivo insuficiente para aumentar la posición.
      return error.message
    }

    if (error.status === 422) {
      return 'Los datos de la posición no son válidos. Revisa el formulario.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo actualizar la posición. Inténtalo nuevamente.'
    }
  }

  return error.message
}

export function EditPositionForm({
  portfolioId,
  position,
  onCancel,
  onUpdated,
}: EditPositionFormProps) {
  const updatePositionMutation = useUpdatePosition(portfolioId, position.id)

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<EditPositionFormValues>({
    resolver: zodResolver(editPositionSchema),
    defaultValues: {
      cantidad: position.cantidad,
      precio_promedio_compra: position.precio_promedio_compra,
    },
  })

  async function submitPosition(values: EditPositionFormValues) {
    if (updatePositionMutation.isPending) {
      return
    }

    const data: PositionUpdateRequest = {
      cantidad: values.cantidad.trim(),
      precio_promedio_compra: values.precio_promedio_compra.trim(),
    }

    try {
      await updatePositionMutation.mutateAsync(data)
      onUpdated()
    } catch {
      // React Query conserva el error en updatePositionMutation.error.
    }
  }

  return (
    <form
      className="portfolio-position-edit"
      onSubmit={(event) => {
        void handleSubmit(submitPosition)(event)
      }}
    >
      <div className="portfolio-position-edit__grid">
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
      </div>

      {updatePositionMutation.isError ? (
        <div className="portfolio-position-form__error" role="alert">
          <strong>No fue posible actualizar la posición.</strong>
          <span>{getUpdatePositionErrorMessage(updatePositionMutation.error)}</span>
        </div>
      ) : null}

      <div className="portfolio-position-form__actions">
        <button
          className="button button--secondary"
          type="button"
          disabled={updatePositionMutation.isPending}
          onClick={onCancel}
        >
          Cancelar
        </button>

        <button
          className="button button--primary"
          type="submit"
          disabled={updatePositionMutation.isPending || !isDirty}
        >
          {updatePositionMutation.isPending ? 'Guardando cambios...' : 'Guardar cambios'}
        </button>
      </div>
    </form>
  )
}
