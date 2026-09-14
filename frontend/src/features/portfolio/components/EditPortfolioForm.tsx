import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type { PortfolioResponse, PortfolioUpdateRequest } from '@/api/types'
import { useUpdatePortfolio } from '@/features/portfolio/hooks/useUpdatePortfolio'

interface EditPortfolioFormProps {
  portfolioId: string
  portfolio: Pick<PortfolioResponse, 'nombre' | 'descripcion'>
  onCancel: () => void
  onUpdated: () => void
}

const editPortfolioSchema = z.object({
  nombre: z
    .string()
    .trim()
    .min(1, 'Ingresa un nombre para el portafolio.')
    .max(150, 'El nombre no puede superar 150 caracteres.'),
  descripcion: z.string().trim().max(2000, 'La descripción no puede superar 2000 caracteres.'),
})

type EditPortfolioFormValues = z.infer<typeof editPortfolioSchema>

function getUpdatePortfolioErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 422) {
      return 'Los datos del portafolio no son válidos. Revisa el formulario e inténtalo nuevamente.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo actualizar el portafolio. Inténtalo nuevamente.'
    }
  }

  return error.message
}

export function EditPortfolioForm({
  portfolioId,
  portfolio,
  onCancel,
  onUpdated,
}: EditPortfolioFormProps) {
  const updatePortfolioMutation = useUpdatePortfolio(portfolioId)

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<EditPortfolioFormValues>({
    resolver: zodResolver(editPortfolioSchema),
    defaultValues: {
      nombre: portfolio.nombre,
      descripcion: portfolio.descripcion ?? '',
    },
  })

  async function submitPortfolio(values: EditPortfolioFormValues) {
    if (updatePortfolioMutation.isPending) {
      return
    }

    const data: PortfolioUpdateRequest = {
      nombre: values.nombre.trim(),
      descripcion: values.descripcion.trim() || null,
    }

    try {
      await updatePortfolioMutation.mutateAsync(data)
      onUpdated()
    } catch {
      // React Query conserva el error en updatePortfolioMutation.error.
    }
  }

  return (
    <section className="portfolio-edit" aria-labelledby="portfolio-edit-title">
      <header className="portfolio-edit__header">
        <div>
          <p className="app__eyebrow">Edición</p>
          <h2 id="portfolio-edit-title">Editar portafolio</h2>
          <p>Modifica únicamente el nombre y la descripción del portafolio.</p>
        </div>
      </header>

      <form
        className="portfolio-edit__form"
        onSubmit={(event) => {
          void handleSubmit(submitPortfolio)(event)
        }}
      >
        <div className="portfolio-edit__grid">
          <label className="portfolio-field">
            <span>Nombre</span>
            <input type="text" maxLength={150} autoComplete="off" {...register('nombre')} />
            {errors.nombre ? (
              <small className="portfolio-field__error">{errors.nombre.message}</small>
            ) : null}
          </label>

          <label className="portfolio-field">
            <span>Descripción</span>
            <textarea rows={5} maxLength={2000} {...register('descripcion')} />
            {errors.descripcion ? (
              <small className="portfolio-field__error">{errors.descripcion.message}</small>
            ) : null}
          </label>
        </div>

        {updatePortfolioMutation.isError ? (
          <div className="portfolio-edit__error" role="alert">
            <strong>No fue posible actualizar el portafolio.</strong>
            <span>{getUpdatePortfolioErrorMessage(updatePortfolioMutation.error)}</span>
          </div>
        ) : null}

        <div className="portfolio-edit__actions">
          <button
            className="button button--secondary"
            type="button"
            disabled={updatePortfolioMutation.isPending}
            onClick={onCancel}
          >
            Cancelar
          </button>

          <button
            className="button button--primary"
            type="submit"
            disabled={updatePortfolioMutation.isPending || !isDirty}
          >
            {updatePortfolioMutation.isPending ? 'Guardando cambios...' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </section>
  )
}
