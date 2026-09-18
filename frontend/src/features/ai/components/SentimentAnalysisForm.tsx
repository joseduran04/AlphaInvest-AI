import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type {
  AnalysisRequestResponse,
  AssetResponse,
  NewsResponse,
  SentimentAnalysisRequestCreate,
} from '@/api/types'
import { useCreateSentimentAnalysis } from '@/features/ai/hooks/useCreateSentimentAnalysis'

interface SentimentAnalysisFormProps {
  assets: AssetResponse[]
  news: NewsResponse[]
  selectedAssetId: string
  newsLoading?: boolean
  newsError?: string
  disabled?: boolean
  onAssetChange: (assetId: string) => void
  onRetryNews?: () => void
  onCreated: (request: AnalysisRequestResponse) => void
}

const sentimentAnalysisSchema = z.object({
  asset_id: z.string().min(1, 'Selecciona un activo.'),
  news_reference_id: z.string().min(1, 'Selecciona una noticia.'),
  reference_date: z.string().min(1, 'Selecciona la fecha de referencia.'),
})

type SentimentAnalysisFormValues = z.infer<typeof sentimentAnalysisSchema>

function getCreateSentimentErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 403) {
      return 'Tu usuario no cuenta con permiso para solicitar análisis de sentimiento.'
    }

    if (error.status === 404) {
      return 'El activo o la noticia seleccionada ya no están disponibles.'
    }

    if (error.status === 409) {
      return 'No fue posible iniciar el análisis debido al estado actual de la solicitud.'
    }

    if (error.status === 422) {
      return 'Los datos enviados no son válidos. Revisa el activo, la noticia y la fecha.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo iniciar el análisis de sentimiento. Inténtalo nuevamente.'
    }
  }

  return error.message
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

export function SentimentAnalysisForm({
  assets,
  news,
  selectedAssetId,
  newsLoading = false,
  newsError,
  disabled = false,
  onAssetChange,
  onRetryNews,
  onCreated,
}: SentimentAnalysisFormProps) {
  const createSentimentMutation = useCreateSentimentAnalysis()

  const {
    register,
    handleSubmit,
    resetField,
    setValue,
    formState: { errors },
  } = useForm<SentimentAnalysisFormValues>({
    resolver: zodResolver(sentimentAnalysisSchema),
    defaultValues: {
      asset_id: selectedAssetId,
      news_reference_id: '',
      reference_date: '',
    },
  })

  useEffect(() => {
    setValue('asset_id', selectedAssetId)
    resetField('news_reference_id')
    resetField('reference_date')
  }, [resetField, selectedAssetId, setValue])

  async function submitAnalysis(values: SentimentAnalysisFormValues) {
    if (createSentimentMutation.isPending || disabled) {
      return
    }

    const data: SentimentAnalysisRequestCreate = {
      asset_id: values.asset_id,
      news_reference_id: values.news_reference_id,
      reference_date: values.reference_date,
    }

    try {
      const request = await createSentimentMutation.mutateAsync(data)
      onCreated(request)
    } catch {
      // React Query conserva el error en createSentimentMutation.error.
    }
  }

  const assetRegistration = register('asset_id')

  return (
    <section className="ai-analysis-form" aria-labelledby="ai-sentiment-form-title">
      <header className="ai-analysis-form__header">
        <div>
          <p className="app__eyebrow">Nuevo análisis</p>
          <h2 id="ai-sentiment-form-title">Analizar sentimiento</h2>
          <p>
            Selecciona un activo y una noticia asociada para evaluar el sentimiento detectado por
            AlphaInvest AI.
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
              disabled={disabled || createSentimentMutation.isPending}
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

          <label className="ai-field ai-field--wide">
            <span>Noticia</span>
            <select
              disabled={
                disabled ||
                createSentimentMutation.isPending ||
                !selectedAssetId ||
                newsLoading ||
                Boolean(newsError)
              }
              {...register('news_reference_id')}
            >
              <option value="">
                {!selectedAssetId
                  ? 'Selecciona primero un activo'
                  : newsLoading
                    ? 'Cargando noticias...'
                    : news.length === 0
                      ? 'No hay noticias disponibles'
                      : 'Selecciona una noticia'}
              </option>

              {news.map((item) => (
                <option key={item.reference_id} value={item.reference_id}>
                  {item.title} · {item.source} · {formatNewsDate(item.published_at)}
                </option>
              ))}
            </select>

            {errors.news_reference_id ? (
              <small className="ai-field__error">{errors.news_reference_id.message}</small>
            ) : null}
          </label>

          <label className="ai-field">
            <span>Fecha de referencia</span>
            <input
              type="date"
              disabled={disabled || createSentimentMutation.isPending}
              {...register('reference_date')}
            />

            {errors.reference_date ? (
              <small className="ai-field__error">{errors.reference_date.message}</small>
            ) : null}
          </label>
        </div>

        {newsError ? (
          <div className="ai-analysis-form__error" role="alert">
            <strong>No fue posible cargar las noticias.</strong>
            <span>{newsError}</span>

            {onRetryNews ? (
              <button className="button button--secondary" type="button" onClick={onRetryNews}>
                Reintentar
              </button>
            ) : null}
          </div>
        ) : null}

        {createSentimentMutation.isError ? (
          <div className="ai-analysis-form__error" role="alert">
            <strong>No fue posible iniciar el análisis.</strong>
            <span>{getCreateSentimentErrorMessage(createSentimentMutation.error)}</span>
          </div>
        ) : null}

        <div className="ai-analysis-form__actions">
          <button
            className="button button--primary"
            type="submit"
            disabled={
              disabled ||
              createSentimentMutation.isPending ||
              assets.length === 0 ||
              !selectedAssetId ||
              news.length === 0
            }
          >
            {createSentimentMutation.isPending ? 'Solicitando análisis...' : 'Analizar sentimiento'}
          </button>
        </div>
      </form>
    </section>
  )
}
