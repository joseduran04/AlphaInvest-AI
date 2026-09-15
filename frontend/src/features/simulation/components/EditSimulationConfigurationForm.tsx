import { zodResolver } from '@hookform/resolvers/zod'
import { useForm, useWatch } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type {
  ContributionFrequency,
  SimulationConfigurationResponse,
  SimulationConfigurationUpdateRequest,
} from '@/api/types'
import { useUpdateSimulationConfiguration } from '@/features/simulation/hooks/useUpdateSimulationConfiguration'

interface EditSimulationConfigurationFormProps {
  configuration: SimulationConfigurationResponse
  onCancel: () => void
  onUpdated: () => void
}

const contributionFrequencies: Array<{
  value: ContributionFrequency
  label: string
}> = [
  { value: 'SEMANAL', label: 'Semanal' },
  { value: 'QUINCENAL', label: 'Quincenal' },
  { value: 'MENSUAL', label: 'Mensual' },
  { value: 'TRIMESTRAL', label: 'Trimestral' },
  { value: 'SEMESTRAL', label: 'Semestral' },
  { value: 'ANUAL', label: 'Anual' },
]

const editSimulationSchema = z
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
      .refine((value) => Number.isFinite(Number(value)) && Number(value) > 0, {
        message: 'El capital inicial debe ser mayor que cero.',
      }),
    moneda_base: z
      .string()
      .trim()
      .length(3, 'La moneda debe tener exactamente 3 caracteres.')
      .regex(/^[A-Za-z]{3}$/, 'La moneda debe contener únicamente letras.'),
    fecha_inicio: z.string().min(1, 'Selecciona la fecha de inicio.'),
    fecha_fin: z.string().min(1, 'Selecciona la fecha final.'),
    aportacion_periodica: z
      .string()
      .trim()
      .min(1, 'Ingresa la aportación periódica.')
      .refine((value) => Number.isFinite(Number(value)) && Number(value) >= 0, {
        message: 'La aportación periódica no puede ser negativa.',
      }),
    frecuencia_aportacion: z.string(),
    comision_porcentaje: z
      .string()
      .trim()
      .min(1, 'Ingresa la comisión.')
      .refine(
        (value) => Number.isFinite(Number(value)) && Number(value) >= 0 && Number(value) <= 100,
        {
          message: 'La comisión debe estar entre 0 y 100.',
        },
      ),
    inflacion_anual: z.string(),
    tasa_libre_riesgo: z.string(),
    numero_escenarios: z
      .string()
      .trim()
      .min(1, 'Ingresa el número de escenarios.')
      .refine(
        (value) =>
          Number.isInteger(Number(value)) && Number(value) >= 1 && Number(value) <= 1_000_000,
        {
          message: 'El número de escenarios debe estar entre 1 y 1,000,000.',
        },
      ),
    semilla_aleatoria: z.string(),
  })
  .superRefine((values, context) => {
    if (values.fecha_inicio && values.fecha_fin && values.fecha_fin <= values.fecha_inicio) {
      context.addIssue({
        code: 'custom',
        path: ['fecha_fin'],
        message: 'La fecha final debe ser posterior a la fecha de inicio.',
      })
    }

    const contribution = Number(values.aportacion_periodica)

    if (Number.isFinite(contribution) && contribution > 0 && !values.frecuencia_aportacion) {
      context.addIssue({
        code: 'custom',
        path: ['frecuencia_aportacion'],
        message: 'Selecciona una frecuencia cuando exista una aportación periódica.',
      })
    }

    for (const [field, value, label] of [
      ['inflacion_anual', values.inflacion_anual, 'La inflación anual'],
      ['tasa_libre_riesgo', values.tasa_libre_riesgo, 'La tasa libre de riesgo'],
    ] as const) {
      if (value.trim() && (!Number.isFinite(Number(value)) || Number(value) <= -100)) {
        context.addIssue({
          code: 'custom',
          path: [field],
          message: `${label} debe ser mayor que -100.`,
        })
      }
    }

    if (values.semilla_aleatoria.trim() && !Number.isInteger(Number(values.semilla_aleatoria))) {
      context.addIssue({
        code: 'custom',
        path: ['semilla_aleatoria'],
        message: 'La semilla aleatoria debe ser un número entero.',
      })
    }
  })

type EditSimulationFormValues = z.infer<typeof editSimulationSchema>

function getUpdateErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return 'La configuración no puede modificarse en su estado actual.'
    }

    if (error.status === 422) {
      return 'Los datos de la simulación no son válidos. Revisa el formulario.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo actualizar la simulación. Inténtalo nuevamente.'
    }
  }

  return error.message
}

export function EditSimulationConfigurationForm({
  configuration,
  onCancel,
  onUpdated,
}: EditSimulationConfigurationFormProps) {
  const updateMutation = useUpdateSimulationConfiguration(configuration.id)

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isDirty },
  } = useForm<EditSimulationFormValues>({
    resolver: zodResolver(editSimulationSchema),
    defaultValues: {
      nombre: configuration.nombre,
      descripcion: configuration.descripcion ?? '',
      capital_inicial: configuration.capital_inicial,
      moneda_base: configuration.moneda_base,
      fecha_inicio: configuration.fecha_inicio,
      fecha_fin: configuration.fecha_fin,
      aportacion_periodica: configuration.aportacion_periodica,
      frecuencia_aportacion: configuration.frecuencia_aportacion ?? '',
      comision_porcentaje: configuration.comision_porcentaje,
      inflacion_anual: configuration.inflacion_anual ?? '',
      tasa_libre_riesgo: configuration.tasa_libre_riesgo ?? '',
      numero_escenarios: String(configuration.numero_escenarios),
      semilla_aleatoria:
        configuration.semilla_aleatoria === null ? '' : String(configuration.semilla_aleatoria),
    },
  })

  const periodicContributionValue = useWatch({
    control,
    name: 'aportacion_periodica',
  })

  const periodicContribution = Number(periodicContributionValue)
  const contributionEnabled = Number.isFinite(periodicContribution) && periodicContribution > 0

  async function submitConfiguration(values: EditSimulationFormValues) {
    if (updateMutation.isPending) {
      return
    }

    const data: SimulationConfigurationUpdateRequest = {
      nombre: values.nombre.trim(),
      descripcion: values.descripcion.trim() || null,
      tipo_simulacion: 'HISTORICA',
      capital_inicial: values.capital_inicial.trim(),
      moneda_base: values.moneda_base.trim().toUpperCase(),
      fecha_inicio: values.fecha_inicio,
      fecha_fin: values.fecha_fin,
      aportacion_periodica: values.aportacion_periodica.trim(),
      frecuencia_aportacion: contributionEnabled
        ? (values.frecuencia_aportacion as ContributionFrequency)
        : null,
      comision_porcentaje: values.comision_porcentaje.trim(),
      inflacion_anual: values.inflacion_anual.trim() || null,
      tasa_libre_riesgo: values.tasa_libre_riesgo.trim() || null,
      numero_escenarios: Number(values.numero_escenarios),
      semilla_aleatoria: values.semilla_aleatoria.trim() ? Number(values.semilla_aleatoria) : null,
    }

    try {
      await updateMutation.mutateAsync(data)
      onUpdated()
    } catch {
      // React Query conserva el error en updateMutation.error.
    }
  }

  return (
    <section className="simulation-edit" aria-labelledby="simulation-edit-title">
      <header className="simulation-edit__header">
        <div>
          <p className="app__eyebrow">Edición</p>
          <h2 id="simulation-edit-title">Editar configuración</h2>
          <p>Modifica los parámetros de la simulación mientras permanezca en estado borrador.</p>
        </div>
      </header>

      <form
        className="simulation-edit__form"
        onSubmit={(event) => {
          void handleSubmit(submitConfiguration)(event)
        }}
      >
        <div className="simulation-form__grid">
          <label className="simulation-field">
            <span>Nombre</span>
            <input type="text" maxLength={150} {...register('nombre')} />
            {errors.nombre ? (
              <small className="simulation-field__error">{errors.nombre.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Tipo</span>
            <select value="HISTORICA" disabled>
              <option value="HISTORICA">Histórica</option>
            </select>
          </label>

          <label className="simulation-field">
            <span>Capital inicial</span>
            <input type="number" min="0" step="any" {...register('capital_inicial')} />
            {errors.capital_inicial ? (
              <small className="simulation-field__error">{errors.capital_inicial.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Moneda base</span>
            <input type="text" maxLength={3} {...register('moneda_base')} />
            {errors.moneda_base ? (
              <small className="simulation-field__error">{errors.moneda_base.message}</small>
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

          <label className="simulation-field">
            <span>Aportación periódica</span>
            <input type="number" min="0" step="any" {...register('aportacion_periodica')} />
            {errors.aportacion_periodica ? (
              <small className="simulation-field__error">
                {errors.aportacion_periodica.message}
              </small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Frecuencia de aportación</span>
            <select disabled={!contributionEnabled} {...register('frecuencia_aportacion')}>
              <option value="">Sin frecuencia</option>
              {contributionFrequencies.map((frequency) => (
                <option key={frequency.value} value={frequency.value}>
                  {frequency.label}
                </option>
              ))}
            </select>
            {errors.frecuencia_aportacion ? (
              <small className="simulation-field__error">
                {errors.frecuencia_aportacion.message}
              </small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Comisión (%)</span>
            <input
              type="number"
              min="0"
              max="100"
              step="any"
              {...register('comision_porcentaje')}
            />
            {errors.comision_porcentaje ? (
              <small className="simulation-field__error">
                {errors.comision_porcentaje.message}
              </small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Inflación anual (%)</span>
            <input type="number" step="any" {...register('inflacion_anual')} />
            {errors.inflacion_anual ? (
              <small className="simulation-field__error">{errors.inflacion_anual.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Tasa libre de riesgo (%)</span>
            <input type="number" step="any" {...register('tasa_libre_riesgo')} />
            {errors.tasa_libre_riesgo ? (
              <small className="simulation-field__error">{errors.tasa_libre_riesgo.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Número de escenarios</span>
            <input
              type="number"
              min="1"
              max="1000000"
              step="1"
              {...register('numero_escenarios')}
            />
            {errors.numero_escenarios ? (
              <small className="simulation-field__error">{errors.numero_escenarios.message}</small>
            ) : null}
          </label>

          <label className="simulation-field">
            <span>Semilla aleatoria</span>
            <input type="number" step="1" {...register('semilla_aleatoria')} />
            {errors.semilla_aleatoria ? (
              <small className="simulation-field__error">{errors.semilla_aleatoria.message}</small>
            ) : null}
          </label>

          <label className="simulation-field simulation-field--wide">
            <span>Descripción</span>
            <textarea rows={5} maxLength={2000} {...register('descripcion')} />
            {errors.descripcion ? (
              <small className="simulation-field__error">{errors.descripcion.message}</small>
            ) : null}
          </label>
        </div>

        {updateMutation.isError ? (
          <div className="simulation-form__error" role="alert">
            <strong>No fue posible actualizar la configuración.</strong>
            <span>{getUpdateErrorMessage(updateMutation.error)}</span>
          </div>
        ) : null}

        <div className="simulation-form__actions">
          <button
            className="button button--secondary"
            type="button"
            disabled={updateMutation.isPending}
            onClick={onCancel}
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
    </section>
  )
}
