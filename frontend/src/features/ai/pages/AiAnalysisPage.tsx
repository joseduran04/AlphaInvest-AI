import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'

import type { AnalysisRequestResponse } from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { AiRequestProgress } from '@/features/ai/components/AiRequestProgress'
import { AssetSentimentThermometer } from '@/features/ai/components/AssetSentimentThermometer'
import { SentimentAnalysisForm } from '@/features/ai/components/SentimentAnalysisForm'
import { SentimentAnalysisResult } from '@/features/ai/components/SentimentAnalysisResult'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'
import { useSentimentAnalysisRequest } from '@/features/ai/hooks/useSentimentAnalysisRequest'
import { useSentimentAnalysisResult } from '@/features/ai/hooks/useSentimentAnalysisResult'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useAssets } from '@/features/market/hooks/useAssets'
import { useAssetNews } from '@/features/news/hooks/useAssetNews'

import '@/styles/ai.css'

function formatRequestStatus(status: AnalysisRequestResponse['status']): string {
  switch (status) {
    case 'PENDIENTE':
      return 'Pendiente'
    case 'EJECUTANDO':
      return 'Ejecutando'
    case 'COMPLETADA':
      return 'Completada'
    case 'FALLIDA':
      return 'Fallida'
    case 'CANCELADA':
      return 'Cancelada'
  }
}

/**
 * Inteligencia artificial de AlphaInvest: análisis de sentimiento de noticias.
 *
 * Los módulos de predicción de tendencia/precio, recomendación y análisis
 * integral se retiraron de la interfaz (métricas insuficientes y riesgo de
 * interpretarse como asesoría de inversión). Siguen disponibles en el backend.
 */
export function AiAnalysisPage() {
  const { hasPermission } = useAuth()
  const queryClient = useQueryClient()

  const canReadAnalysis = hasPermission('analisis.leer')
  const canReadAssets = hasPermission('activos.leer')
  const canRequestAnalysis = hasPermission('analisis.solicitar')
  const canReadNews = hasPermission('noticias.leer')

  const [assetId, setAssetId] = useState('')
  const [requestId, setRequestId] = useState<string | null>(null)

  const assetsQuery = useAssets(
    {
      status: 'ACTIVO',
      limit: 100,
      offset: 0,
    },
    canReadAnalysis && canReadAssets,
  )

  const newsQuery = useAssetNews(
    assetId || null,
    {
      limit: 100,
      offset: 0,
    },
    canReadNews,
  )

  const requestQuery = useSentimentAnalysisRequest(requestId, canReadAnalysis)
  const requestStatus = requestQuery.data?.status

  const resultQuery = useSentimentAnalysisResult(
    requestId,
    canReadAnalysis && requestStatus === 'COMPLETADA',
  )

  const assets = useMemo(() => assetsQuery.data?.items ?? [], [assetsQuery.data?.items])
  const news = useMemo(() => newsQuery.data?.items ?? [], [newsQuery.data?.items])

  const selectedAsset = useMemo(
    () => assets.find((asset) => asset.id === assetId),
    [assets, assetId],
  )

  const resultAsset = useMemo(
    () => assets.find((asset) => asset.id === resultQuery.data?.asset_id),
    [assets, resultQuery.data?.asset_id],
  )

  const resultNews = useMemo(
    () => news.find((item) => item.reference_id === resultQuery.data?.news_reference_id),
    [news, resultQuery.data?.news_reference_id],
  )

  // Un análisis nuevo cambia el termómetro del activo.
  const completedAssetId = resultQuery.data?.asset_id

  useEffect(() => {
    if (completedAssetId) {
      void queryClient.invalidateQueries({
        queryKey: aiQueryKeys.assetSentimentSummary(completedAssetId),
      })
    }
  }, [completedAssetId, queryClient])

  if (!canReadAnalysis) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar análisis inteligentes."
      />
    )
  }

  return (
    <section className="ai-page">
      <header className="ai-page__header">
        <div>
          <p className="app__eyebrow">Inteligencia artificial</p>
          <h1>Sentimiento de noticias</h1>
          <p className="app__description">
            Un modelo de lenguaje lee noticias financieras y detecta si su tono es positivo, neutral
            o negativo para la empresa. Es una herramienta educativa: describe cómo están escritas
            las noticias y no recomienda comprar ni vender.
          </p>
        </div>

        {requestId ? (
          <button
            className="button button--secondary"
            type="button"
            onClick={() => setRequestId(null)}
          >
            Nuevo análisis
          </button>
        ) : null}
      </header>

      {!canReadAssets ? (
        <PageErrorState
          title="Acceso restringido"
          message="Tu usuario no cuenta con permiso para consultar activos financieros."
        />
      ) : assetsQuery.isPending ? (
        <PageLoadingState message="Cargando activos disponibles..." />
      ) : assetsQuery.isError ? (
        <PageErrorState
          title="No fue posible cargar los activos"
          message={assetsQuery.error.message}
          onRetry={() => {
            void assetsQuery.refetch()
          }}
        />
      ) : requestId === null ? (
        canRequestAnalysis ? (
          <SentimentAnalysisForm
            assets={assets}
            news={news}
            selectedAssetId={assetId}
            newsLoading={newsQuery.isPending && Boolean(assetId)}
            newsError={
              !canReadNews
                ? 'Tu usuario no cuenta con permiso para consultar noticias.'
                : newsQuery.isError
                  ? newsQuery.error.message
                  : undefined
            }
            onAssetChange={setAssetId}
            onRetryNews={() => {
              void newsQuery.refetch()
            }}
            onCreated={(request) => setRequestId(request.id)}
          />
        ) : (
          <PageErrorState
            title="Solicitud de análisis restringida"
            message="Puedes consultar análisis, pero tu usuario no cuenta con permiso para solicitar nuevos análisis."
          />
        )
      ) : (
        <section className="ai-request">
          <header className="ai-request__header">
            <div>
              <p className="app__eyebrow">Solicitud de análisis</p>
              <h2>Procesamiento del sentimiento</h2>
            </div>

            {requestStatus ? (
              <span
                className={`ai-request-status ai-request-status--${requestStatus.toLowerCase()}`}
              >
                {formatRequestStatus(requestStatus)}
              </span>
            ) : null}
          </header>

          {requestQuery.isPending ? (
            <PageLoadingState message="Consultando estado del análisis..." />
          ) : requestQuery.isError ? (
            <PageErrorState
              title="No fue posible consultar el análisis"
              message={requestQuery.error.message}
              onRetry={() => {
                void requestQuery.refetch()
              }}
            />
          ) : requestQuery.data.status === 'PENDIENTE' ||
            requestQuery.data.status === 'EJECUTANDO' ? (
            <AiRequestProgress
              status={requestQuery.data.status}
              progressPercentage={requestQuery.data.progress_percentage}
              pendingTitle="Análisis pendiente"
              pendingDescription="La solicitud está esperando ser procesada por el motor de inteligencia artificial."
              executingTitle="Leyendo la noticia"
              executingDescription="El modelo está procesando el contenido de la noticia para determinar su tono."
            />
          ) : requestQuery.data.status === 'FALLIDA' ? (
            <PageErrorState
              title="El análisis no pudo completarse"
              message={
                requestQuery.data.error_message ??
                'El motor de inteligencia artificial reportó un error durante el procesamiento.'
              }
            />
          ) : requestQuery.data.status === 'CANCELADA' ? (
            <PageErrorState
              title="Análisis cancelado"
              message="La solicitud fue cancelada antes de generar un resultado."
            />
          ) : resultQuery.isPending ? (
            <PageLoadingState message="Cargando resultado del análisis de sentimiento..." />
          ) : resultQuery.isError ? (
            <PageErrorState
              title="No fue posible cargar el resultado"
              message={resultQuery.error.message}
              onRetry={() => {
                void resultQuery.refetch()
              }}
            />
          ) : (
            <SentimentAnalysisResult
              result={resultQuery.data}
              asset={resultAsset}
              news={resultNews}
            />
          )}
        </section>
      )}

      {selectedAsset ? <AssetSentimentThermometer asset={selectedAsset} /> : null}
    </section>
  )
}
