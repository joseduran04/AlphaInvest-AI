import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type { PortfolioCreateRequest } from '@/api/types'
import { useCreatePortfolio } from '@/features/portfolio/hooks/useCreatePortfolio'

interface CreatePortfolioFormProps {
  onCancel: () => void
  onCreated: () => void
}

const createPortfolioSchema = z.object({
  nombre: z
    .string()
    .trim()
    .min(1, 'Ingresa un nombre para el portafolio.')
    .max(150, 'El nombre no puede superar 150 caracteres.'),
  descripcion: z.string().trim().max(2000, 'La descripción no puede superar 2000 caracteres.'),
  moneda_base: z
    .string()
    .trim()
    .length(3, 'La moneda debe contener exactamente tres letras.')
    .regex(/^[A-Za-z]{3}$/, 'Utiliza únicamente letras para la moneda.'),
  capital_inicial: z
    .string()
    .trim()
    .min(1, 'Ingresa el capital inicial.')
    .refine((value) => {
      const amount = Number(value)

      return Number.isFinite(amount) && amount >= 0
    }, 'El capital inicial debe ser un número mayor o igual a cero.'),
  tipo: z.enum(['VIRTUAL', 'SIMULADO']),
  fecha_inicio: z.string(),
})

type CreatePortfolioFormValues = z.infer<typeof createPortfolioSchema>

const defaultValues: CreatePortfolioFormValues = {
  nombre: '',
  descripcion: '',
  moneda_base: 'USD',
  capital_inicial: '',
  tipo: 'VIRTUAL',
  fecha_inicio: '',
}

function getCreatePortfolioErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return 'No fue posible crear el portafolio porque existe un conflicto con los datos registrados.'
    }

    if (error.status === 422) {
      return 'Los datos del portafolio no son válidos. Revisa el formulario e inténtalo nuevamente.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo crear el portafolio. Inténtalo nuevamente.'
    }
  }

  return error.message
}

export function CreatePortfolioForm({ onCancel, onCreated }: CreatePortfolioFormProps) {
  const createPortfolioMutation = useCreatePortfolio()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreatePortfolioFormValues>({
    resolver: zodResolver(createPortfolioSchema),
    defaultValues,
  })

  async function submitPortfolio(values: CreatePortfolioFormValues) {
    if (createPortfolioMutation.isPending) {
      return
    }

    const data: PortfolioCreateRequest = {
      nombre: values.nombre.trim(),
      descripcion: values.descripcion.trim() || null,
      moneda_base: values.moneda_base.trim().toUpperCase(),
      capital_inicial: values.capital_inicial.trim(),
      tipo: values.tipo,
      fecha_inicio: values.fecha_inicio || null,
    }

    try {
      await createPortfolioMutation.mutateAsync(data)
      onCreated()
    } catch {
      // React Query conserva el error en createPortfolioMutation.error.
    }
  }

  return (
    <section className="portfolio-create" aria-labelledby="portfolio-create-title">
      <header className="portfolio-create__header">
        <div>
          <p className="app__eyebrow">Nuevo portafolio</p>
          <h2 id="portfolio-create-title">Crear portafolio</h2>
          <p>
            Registra un portafolio virtual o simulado para organizar posiciones y dar seguimiento a
            su evolución.
          </p>
        </div>
      </header>

      <form
        className="portfolio-create__form"
        onSubmit={(event) => {
          void handleSubmit(submitPortfolio)(event)
        }}
      >
        <div className="portfolio-create__grid">
          <label className="portfolio-field portfolio-field--wide">
            <span>Nombre</span>
            <input type="text" maxLength={150} autoComplete="off" {...register('nombre')} />
            {errors.nombre ? (
              <small className="portfolio-field__error">{errors.nombre.message}</small>
            ) : null}
          </label>

          <label className="portfolio-field portfolio-field--wide">
            <span>Descripción</span>
            <textarea rows={4} maxLength={2000} {...register('descripcion')} />
            {errors.descripcion ? (
              <small className="portfolio-field__error">{errors.descripcion.message}</small>
            ) : null}
          </label>

          <label className="portfolio-field">
            <span>Moneda base</span>
            <input type="text" maxLength={3} autoComplete="off" {...register('moneda_base')} />
            {errors.moneda_base ? (
              <small className="portfolio-field__error">{errors.moneda_base.message}</small>
            ) : null}
          </label>

          <label className="portfolio-field">
            <span>Capital inicial</span>
            <input
              type="number"
              min="0"
              step="0.01"
              inputMode="decimal"
              {...register('capital_inicial')}
            />
            {errors.capital_inicial ? (
              <small className="portfolio-field__error">{errors.capital_inicial.message}</small>
            ) : null}
          </label>

          <label className="portfolio-field">
            <span>Tipo</span>
            <select {...register('tipo')}>
              <option value="VIRTUAL">Virtual</option>
              <option value="SIMULADO">Simulado</option>
            </select>
          </label>

          <label className="portfolio-field">
            <span>Fecha de inicio</span>
            <input type="date" {...register('fecha_inicio')} />
          </label>
        </div>

        {createPortfolioMutation.isError ? (
          <div className="portfolio-create__error" role="alert">
            <strong>No fue posible crear el portafolio.</strong>
            <span>{getCreatePortfolioErrorMessage(createPortfolioMutation.error)}</span>
          </div>
        ) : null}

        <div className="portfolio-create__actions">
          <button
            className="button button--secondary"
            type="button"
            disabled={createPortfolioMutation.isPending}
            onClick={onCancel}
          >
            Cancelar
          </button>

          <button
            className="button button--primary"
            type="submit"
            disabled={createPortfolioMutation.isPending}
          >
            {createPortfolioMutation.isPending ? 'Creando portafolio...' : 'Crear portafolio'}
          </button>
        </div>
      </form>
    </section>
  )
}
