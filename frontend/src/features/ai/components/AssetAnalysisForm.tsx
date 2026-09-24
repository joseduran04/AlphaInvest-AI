import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { ApiError } from '@/api/errors'
import type {
  AnalysisRequestResponse,
  AnalysisHorizon,
  AssetAnalysisRequestCreate,
  AssetResponse,
} from '@/api/types'
import { useCreateAssetAnalysis } from '@/features/ai/hooks/useCreateAssetAnalysis'
import { ANALYSIS_HORIZON_OPTIONS } from '@/lib/aiModelCards'

interface AssetAnalysisFormProps {
  assets: AssetResponse[]
  disabled?: boolean
  onCreated: (request: AnalysisRequestResponse) => void
}

const assetAnalysisSchema = z.object({
  asset_id: z.string().min(1, 'Selecciona un activo.'),
  horizon: z.enum(['INTRADIA', 'CORTO_PLAZO', 'MEDIANO_PLAZO', 'LARGO_PLAZO']),
  reference_date: z.string().min(1, 'Selecciona la fecha de referencia.'),
})

type AssetAnalysisFormValues = z.infer<typeof assetAnalysisSchema>

const defaultValues: AssetAnalysisFormValues = {
  asset_id: '',
  horizon: 'CORTO_PLAZO',
  reference_date: '',
}

function getCreateAnalysisErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 403) {
      return 'Tu usuario no cuenta con permiso para solicitar análisis.'
    }

    if (error.status === 404) {
      return 'El activo seleccionado ya no está disponible.'
    }

    if (error.status === 409) {
      return 'No fue posible iniciar el análisis debido al estado actual de la solicitud.'
    }

    if (error.status === 422) {
      return 'Los datos enviados no son válidos. Revisa el activo, horizonte y fecha.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo iniciar el análisis. Inténtalo nuevamente.'
    }
  }

  return error.message
}

export function AssetAnalysisForm({ assets, disabled = false, onCreated }: AssetAnalysisFormProps) {
  const createAnalysisMutation = useCreateAssetAnalysis()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AssetAnalysisFormValues>({
    resolver: zodResolver(assetAnalysisSchema),
    defaultValues,
  })

  async function submitAnalysis(values: AssetAnalysisFormValues) {
    if (createAnalysisMutation.isPending || disabled) {
      return
    }

    const data: AssetAnalysisRequestCreate = {
      asset_id: values.asset_id,
      horizon: values.horizon as AnalysisHorizon,
      reference_date: values.reference_date,
    }

    try {
      const request = await createAnalysisMutation.mutateAsync(data)
      onCreated(request)
    } catch {
      // React Query conserva el error en createAnalysisMutation.error.
    }
  }

  return (
    <section className="ai-analysis-form" aria-labelledby="ai-analysis-form-title">
      <header className="ai-analysis-form__header">
        <div>
          <p className="app__eyebrow">Nuevo análisis</p>
          <h2 id="ai-analysis-form-title">Analizar activo</h2>
          <p>
            Selecciona un instrumento, horizonte y fecha de referencia para solicitar una predicción
            al motor de AlphaInvest AI.
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
              disabled={disabled || createAnalysisMutation.isPending}
              {...register('asset_id')}
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
            <select
              disabled={disabled || createAnalysisMutation.isPending}
              {...register('horizon')}
            >
              {ANALYSIS_HORIZON_OPTIONS.map((option) => (
                <option key={option.value} value={option.value} disabled={!option.supported}>
                  {option.label}
                </option>
              ))}
            </select>
            <small className="metric-hint">
              Solo el horizonte de corto plazo (5 sesiones) tiene un modelo entrenado.
            </small>
          </label>

          <label className="ai-field">
            <span>Fecha de referencia</span>
            <input
              type="date"
              disabled={disabled || createAnalysisMutation.isPending}
              {...register('reference_date')}
            />

            {errors.reference_date ? (
              <small className="ai-field__error">{errors.reference_date.message}</small>
            ) : null}
          </label>
        </div>

        {createAnalysisMutation.isError ? (
          <div className="ai-analysis-form__error" role="alert">
            <strong>No fue posible iniciar el análisis.</strong>
            <span>{getCreateAnalysisErrorMessage(createAnalysisMutation.error)}</span>
          </div>
        ) : null}

        <div className="ai-analysis-form__actions">
          <button
            className="button button--primary"
            type="submit"
            disabled={disabled || createAnalysisMutation.isPending || assets.length === 0}
          >
            {createAnalysisMutation.isPending ? 'Solicitando análisis...' : 'Iniciar análisis'}
          </button>
        </div>
      </form>
    </section>
  )
}
