import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import type { AnalysisHorizon, AssetResponse } from '@/api/types'

const recommendationFormSchema = z.object({
  asset_id: z.string().uuid('Selecciona un activo válido'),
  horizon: z.enum(['INTRADIA', 'CORTO_PLAZO', 'MEDIANO_PLAZO', 'LARGO_PLAZO']),
  reference_date: z.string().min(1, 'Selecciona una fecha de referencia'),
})

type RecommendationFormValues = z.infer<typeof recommendationFormSchema>

export interface RecommendationFormSubmission {
  asset_id: string
  horizon: AnalysisHorizon
  reference_date: string
}

interface RecommendationFormProps {
  assets: AssetResponse[]
  disabled?: boolean
  onSubmit: (data: RecommendationFormSubmission) => void | Promise<void>
}

export function RecommendationForm({
  assets,
  disabled = false,
  onSubmit,
}: RecommendationFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RecommendationFormValues>({
    resolver: zodResolver(recommendationFormSchema),
    defaultValues: {
      asset_id: '',
      horizon: 'CORTO_PLAZO',
      reference_date: '',
    },
  })

  async function submit(values: RecommendationFormValues) {
    await onSubmit({
      asset_id: values.asset_id,
      horizon: values.horizon,
      reference_date: values.reference_date,
    })
  }

  return (
    <form
      className="ai-analysis-form"
      onSubmit={(event) => {
        void handleSubmit(submit)(event)
      }}
    >
      <header className="ai-analysis-form__header">
        <div>
          <p className="app__eyebrow">Recomendación inteligente</p>
          <h2>Generar recomendación</h2>
        </div>

        <p>
          AlphaInvest AI generará primero la predicción necesaria y después evaluará las señales
          disponibles para construir una recomendación educativa.
        </p>
      </header>

      <div className="ai-analysis-form__grid">
        <label className="ai-field">
          <span>Activo</span>
          <select {...register('asset_id')} disabled={disabled || isSubmitting}>
            <option value="">Selecciona un activo</option>
            {assets.map((asset) => (
              <option key={asset.id} value={asset.id}>
                {asset.symbol} · {asset.name}
              </option>
            ))}
          </select>
          {errors.asset_id ? <small>{errors.asset_id.message}</small> : null}
        </label>

        <label className="ai-field">
          <span>Horizonte</span>
          <select {...register('horizon')} disabled={disabled || isSubmitting}>
            <option value="INTRADIA">Intradía</option>
            <option value="CORTO_PLAZO">Corto plazo</option>
            <option value="MEDIANO_PLAZO">Mediano plazo</option>
            <option value="LARGO_PLAZO">Largo plazo</option>
          </select>
          {errors.horizon ? <small>{errors.horizon.message}</small> : null}
        </label>

        <label className="ai-field">
          <span>Fecha de referencia</span>
          <input type="date" {...register('reference_date')} disabled={disabled || isSubmitting} />
          {errors.reference_date ? <small>{errors.reference_date.message}</small> : null}
        </label>
      </div>

      <footer className="ai-analysis-form__actions">
        <button
          className="button button--primary"
          type="submit"
          disabled={disabled || isSubmitting || assets.length === 0}
        >
          {isSubmitting ? 'Preparando análisis...' : 'Generar recomendación'}
        </button>
      </footer>
    </form>
  )
}
