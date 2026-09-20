import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import type { AnalysisHorizon, AssetResponse, PortfolioResponse } from '@/api/types'

const recommendationFormSchema = z.object({
  asset_id: z.string().uuid('Selecciona un activo válido'),
  portfolio_id: z.union([z.string().uuid('Selecciona un portafolio válido'), z.literal('')]),
  horizon: z.enum(['INTRADIA', 'CORTO_PLAZO', 'MEDIANO_PLAZO', 'LARGO_PLAZO']),
  reference_date: z.string().min(1, 'Selecciona una fecha de referencia'),
})

type RecommendationFormValues = z.infer<typeof recommendationFormSchema>

export interface RecommendationFormSubmission {
  asset_id: string
  portfolio_id?: string
  horizon: AnalysisHorizon
  reference_date: string
}

interface RecommendationFormProps {
  assets: AssetResponse[]
  portfolios: PortfolioResponse[]
  portfoliosLoading?: boolean
  portfoliosError?: string
  disabled?: boolean
  onRetryPortfolios?: () => void
  onSubmit: (data: RecommendationFormSubmission) => void | Promise<void>
}

export function RecommendationForm({
  assets,
  portfolios,
  portfoliosLoading = false,
  portfoliosError,
  disabled = false,
  onRetryPortfolios,
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
      portfolio_id: '',
      horizon: 'CORTO_PLAZO',
      reference_date: '',
    },
  })

  async function submit(values: RecommendationFormValues) {
    await onSubmit({
      asset_id: values.asset_id,
      portfolio_id: values.portfolio_id || undefined,
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
          <span>Portafolio (opcional)</span>

          <select
            {...register('portfolio_id')}
            disabled={disabled || isSubmitting || portfoliosLoading}
          >
            <option value="">
              {portfoliosLoading ? 'Cargando portafolios...' : 'Sin portafolio específico'}
            </option>

            {portfolios.map((portfolio) => (
              <option key={portfolio.id} value={portfolio.id}>
                {portfolio.nombre} · {portfolio.moneda_base}
              </option>
            ))}
          </select>

          {errors.portfolio_id ? <small>{errors.portfolio_id.message}</small> : null}

          {!portfoliosLoading && !portfoliosError ? (
            <small>
              Selecciona un portafolio si deseas contextualizar la recomendación con tu posición
              actual en el activo.
            </small>
          ) : null}
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

      {portfoliosError ? (
        <div className="ai-analysis-form__error" role="alert">
          <strong>No fue posible cargar tus portafolios.</strong>
          <span>{portfoliosError}</span>

          {onRetryPortfolios ? (
            <button
              className="button button--secondary"
              type="button"
              onClick={onRetryPortfolios}
              disabled={disabled || isSubmitting}
            >
              Reintentar
            </button>
          ) : null}
        </div>
      ) : null}

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
