import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type { SimulationConfigurationCreateRequest } from '@/api/types'
import { useCreateSimulationConfiguration } from '@/features/simulation/hooks/useCreateSimulationConfiguration'

interface CreateSimulationConfigurationFormProps {
  onCancel: () => void
  onCreated: () => void
}

const createSimulationConfigurationSchema = z
  .object({
    nombre: z
      .string()
      .trim()
      .min(1, 'Ingresa un nombre para la simulación.')
      .max(150, 'El nombre no puede superar 150 caracteres.'),
    descripcion: z.string().trim().max(2000, 'La descripción no puede superar 2000 caracteres.'),
    capital_inicial: z
      .string()
      .trim()
      .min(1, 'Ingresa el capital inicial.')
      .refine((value) => {
        const amount = Number(value)

        return Number.isFinite(amount) && amount > 0
      }, 'El capital inicial debe ser mayor que cero.'),
    moneda_base: z
      .string()
      .trim()
      .length(3, 'La moneda debe contener exactamente tres letras.')
      .regex(/^[A-Za-z]{3}$/, 'Utiliza únicamente letras para la moneda.'),
    fecha_inicio: z.string().min(1, 'Selecciona la fecha de inicio.'),
    fecha_fin: z.string().min(1, 'Selecciona la fecha final.'),
  })
  .refine(
    (values) => {
      if (!values.fecha_inicio || !values.fecha_fin) {
        return true
      }

      return values.fecha_fin > values.fecha_inicio
    },
    {
      message: 'La fecha final debe ser posterior a la fecha de inicio.',
      path: ['fecha_fin'],
    },
  )

type CreateSimulationConfigurationFormValues = z.infer<typeof createSimulationConfigurationSchema>

const defaultValues: CreateSimulationConfigurationFormValues = {
  nombre: '',
  descripcion: '',
  capital_inicial: '',
  moneda_base: 'USD',
  fecha_inicio: '',
  fecha_fin: '',
}

function getCreateSimulationErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return 'No fue posible crear la configuración porque existe un conflicto con los datos registrados.'
    }

    if (error.status === 422) {
      return 'Los datos de la simulación no son válidos. Revisa el formulario e inténtalo nuevamente.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo crear la configuración. Inténtalo nuevamente.'
    }
  }

  return error.message
}

export function CreateSimulationConfigurationForm({
  onCancel,
  onCreated,
}: CreateSimulationConfigurationFormProps) {
  const createSimulationMutation = useCreateSimulationConfiguration()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateSimulationConfigurationFormValues>({
    resolver: zodResolver(createSimulationConfigurationSchema),
    defaultValues,
  })

  async function submitConfiguration(values: CreateSimulationConfigurationFormValues) {
    if (createSimulationMutation.isPending) {
      return
    }

    const data: SimulationConfigurationCreateRequest = {
      nombre: values.nombre.trim(),
      descripcion: values.descripcion.trim() || undefined,
      tipo_simulacion: 'HISTORICA',
      capital_inicial: values.capital_inicial.trim(),
      moneda_base: values.moneda_base.trim().toUpperCase(),
      fecha_inicio: values.fecha_inicio,
      fecha_fin: values.fecha_fin,
      aportacion_periodica: 0,
      comision_porcentaje: 0,
      numero_escenarios: 1,
    }

    try {
      await createSimulationMutation.mutateAsync(data)
      onCreated()
    } catch {
      // React Query conserva el error en createSimulationMutation.error.
    }
  }

  return (
    <section className="simulation-create" aria-labelledby="simulation-create-title">
      <header className="simulation-create__header">
        <div>
          <p className="app__eyebrow">Nueva simulación</p>
          <h2 id="simulation-create-title">Crear configuración histórica</h2>
          <p>
            Define el periodo y capital base de la simulación. Los activos y su distribución se
            configurarán posteriormente.
          </p>
        </div>
      </header>

      <div className="simulation-create__notice">
        <strong>Tipo de simulación</strong>
        <span>
          La versión actual ejecuta simulaciones históricas. Monte Carlo, proyección y escenarios
          permanecerán disponibles para futuras extensiones del motor.
        </span>
      </div>

      <form
        className="simulation-create__form"
        onSubmit={(event) => {
          void handleSubmit(submitConfiguration)(event)
        }}
      >
        <div className="simulation-create__grid">
          <label className="simulation-field simulation-field--wide">
            <span>Nombre</span>
            <input type="text" maxLength={150} autoComplete="off" {...register('nombre')} />

            {errors.nombre ? (
              <small className="simulation-field__error">{errors.nombre.message}</small>
            ) : null}
          </label>

          <label className="simulation-field simulation-field--wide">
            <span>Descripción</span>
            <textarea rows={4} maxLength={2000} {...register('descripcion')} />

            {errors.descripcion ? (
              <small className="simulation-field__error">{errors.descripcion.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Tipo</span>
            <select value="HISTORICA" disabled>
              <option value="HISTORICA">Histórica</option>
            </select>
          </label>

          <label className="simulation-field">
            <span>Moneda base</span>
            <input type="text" maxLength={3} autoComplete="off" {...register('moneda_base')} />

            {errors.moneda_base ? (
              <small className="simulation-field__error">{errors.moneda_base.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Capital inicial</span>
            <input
              type="number"
              min="0.01"
              step="0.01"
              inputMode="decimal"
              {...register('capital_inicial')}
            />

            {errors.capital_inicial ? (
              <small className="simulation-field__error">{errors.capital_inicial.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Fecha de inicio</span>
            <input type="date" {...register('fecha_inicio')} />

            {errors.fecha_inicio ? (
              <small className="simulation-field__error">{errors.fecha_inicio.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Fecha final</span>
            <input type="date" {...register('fecha_fin')} />

            {errors.fecha_fin ? (
              <small className="simulation-field__error">{errors.fecha_fin.message}</small>
            ) : null}
          </label>
        </div>

        {createSimulationMutation.isError ? (
          <div className="simulation-create__error" role="alert">
            <strong>No fue posible crear la configuración.</strong>
            <span>{getCreateSimulationErrorMessage(createSimulationMutation.error)}</span>
          </div>
        ) : null}

        <div className="simulation-create__actions">
          <button
            className="button button--secondary"
            type="button"
            disabled={createSimulationMutation.isPending}
            onClick={onCancel}
          >
            Cancelar
          </button>

          <button
            className="button button--primary"
            type="submit"
            disabled={createSimulationMutation.isPending}
          >
            {createSimulationMutation.isPending
              ? 'Creando configuración...'
              : 'Crear configuración'}
          </button>
        </div>
      </form>
    </section>
  )
}
