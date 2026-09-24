import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import type { AnalysisHorizon, AssetResponse, NewsResponse } from '@/api/types'
import { ANALYSIS_HORIZON_OPTIONS } from '@/lib/aiModelCards'

const integralAnalysisSchema = z.object({
  asset_id: z.string().uuid('Selecciona un activo válido.'),
  horizon: z.enum(['INTRADIA', 'CORTO_PLAZO', 'MEDIANO_PLAZO', 'LARGO_PLAZO']),
  reference_date: z.string().min(1, 'Selecciona la fecha de referencia.'),
  news_reference_id: z.string(),
})

type IntegralAnalysisFormValues = z.infer<typeof integralAnalysisSchema>

export interface IntegralAnalysisFormSubmission {
  asset_id: string
  horizon: AnalysisHorizon
  reference_date: string
  news_reference_id: string | null
}

interface IntegralAnalysisFormProps {
  assets: AssetResponse[]
  news: NewsResponse[]
  selectedAssetId: string
  newsLoading?: boolean
  newsError?: string
  disabled?: boolean
  onAssetChange: (assetId: string) => void
  onRetryNews?: () => void
  onSubmit: (data: IntegralAnalysisFormSubmission) => Promise<void> | void
}

function formatNewsDate(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(date)
}

export function IntegralAnalysisForm({
  assets,
  news,
  selectedAssetId,
  newsLoading = false,
  newsError,
  disabled = false,
  onAssetChange,
  onRetryNews,
  onSubmit,
}: IntegralAnalysisFormProps) {
  const {
    register,
    handleSubmit,
    resetField,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<IntegralAnalysisFormValues>({
    resolver: zodResolver(integralAnalysisSchema),
    defaultValues: {
      asset_id: selectedAssetId,
      horizon: 'CORTO_PLAZO',
      reference_date: '',
      news_reference_id: '',
    },
  })

  useEffect(() => {
    setValue('asset_id', selectedAssetId)
    resetField('news_reference_id')
  }, [resetField, selectedAssetId, setValue])

  const assetRegistration = register('asset_id')

  async function submitAnalysis(values: IntegralAnalysisFormValues) {
    if (disabled || isSubmitting) {
      return
    }

    await onSubmit({
      asset_id: values.asset_id,
      horizon: values.horizon,
      reference_date: values.reference_date,
      news_reference_id: values.news_reference_id || null,
    })
  }

  return (
    <section className="ai-analysis-form" aria-labelledby="ai-integral-form-title">
      <header className="ai-analysis-form__header">
        <div>
          <p className="app__eyebrow">Nuevo análisis</p>
          <h2 id="ai-integral-form-title">Análisis integral</h2>
          <p>
            Combina una predicción del activo con una noticia opcional para generar una
            recomendación integral y explicable.
          </p>
        </div>
      </header>

      <form
        className="ai-analysis-form__form"
        onSubmit={(event) => {
          void handleSubmit(submitAnalysis)(event)
        }}
      >
        <div className="ai-analysis-form__grid">
          <label className="ai-field ai-field--wide">
            <span>Activo</span>
            <select
              disabled={disabled || isSubmitting}
              {...assetRegistration}
              onChange={(event) => {
                void assetRegistration.onChange(event)
                onAssetChange(event.target.value)
              }}
            >
              <option value="">Selecciona un activo</option>

              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.symbol} · {asset.name}
                </option>
              ))}
            </select>

            {errors.asset_id ? (
              <small className="ai-field__error">{errors.asset_id.message}</small>
            ) : null}
          </label>

          <label className="ai-field">
            <span>Horizonte</span>
            <select disabled={disabled || isSubmitting} {...register('horizon')}>
              {ANALYSIS_HORIZON_OPTIONS.map((option) => (
                <option key={option.value} value={option.value} disabled={!option.supported}>
                  {option.label}
                </option>
              ))}
            </select>
            <small className="metric-hint">
              Solo el horizonte de corto plazo (5 sesiones) tiene un modelo entrenado.
            </small>

            {errors.horizon ? (
              <small className="ai-field__error">{errors.horizon.message}</small>
            ) : null}
          </label>

          <label className="ai-field">
            <span>Fecha de referencia</span>
            <input
              type="date"
              disabled={disabled || isSubmitting}
              {...register('reference_date')}
            />

            {errors.reference_date ? (
              <small className="ai-field__error">{errors.reference_date.message}</small>
            ) : null}
          </label>

          <label className="ai-field ai-field--wide">
            <span>Noticia para sentimiento (opcional)</span>
            <select
              disabled={disabled || isSubmitting || !selectedAssetId || newsLoading}
              {...register('news_reference_id')}
            >
              <option value="">
                {!selectedAssetId
                  ? 'Selecciona primero un activo'
                  : newsLoading
                    ? 'Cargando noticias...'
                    : newsError
                      ? 'Noticias no disponibles — continuar sin sentimiento'
                      : news.length === 0
                        ? 'Continuar sin análisis de sentimiento'
                        : 'Sin noticia — continuar sólo con predicción'}
              </option>

              {news.map((item) => (
                <option key={item.reference_id} value={item.reference_id}>
                  {item.title} · {item.source} · {formatNewsDate(item.published_at)}
                </option>
              ))}
            </select>
          </label>
        </div>

        {newsError ? (
          <div className="ai-analysis-form__error" role="alert">
            <strong>No fue posible cargar las noticias.</strong>
            <span>
              Puedes reintentar la consulta o continuar el análisis integral sin sentimiento.
            </span>

            {onRetryNews ? (
              <button className="button button--secondary" type="button" onClick={onRetryNews}>
                Reintentar
              </button>
            ) : null}
          </div>
        ) : null}

        <div className="ai-analysis-form__actions">
          <button
            className="button button--primary"
            type="submit"
            disabled={disabled || isSubmitting || assets.length === 0}
          >
            {isSubmitting ? 'Preparando análisis...' : 'Generar análisis integral'}
          </button>
        </div>
      </form>
    </section>
  )
}
