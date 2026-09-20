import { useEffect, useMemo, useRef, useState } from 'react'

import type {
  AnalysisRequestResponse,
  AssetAnalysisRequestCreate,
  SentimentAnalysisRequestCreate,
} from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { AiRequestProgress } from '@/features/ai/components/AiRequestProgress'
import { AssetAnalysisForm } from '@/features/ai/components/AssetAnalysisForm'
import { AssetAnalysisResult } from '@/features/ai/components/AssetAnalysisResult'
import {
  IntegralAnalysisForm,
  type IntegralAnalysisFormSubmission,
} from '@/features/ai/components/IntegralAnalysisForm'
import {
  RecommendationForm,
  type RecommendationFormSubmission,
} from '@/features/ai/components/RecommendationForm'
import { RecommendationResult } from '@/features/ai/components/RecommendationResult'
import { SentimentAnalysisForm } from '@/features/ai/components/SentimentAnalysisForm'
import { SentimentAnalysisResult } from '@/features/ai/components/SentimentAnalysisResult'
import { useAssetAnalysisRequest } from '@/features/ai/hooks/useAssetAnalysisRequest'
import { useAssetAnalysisResult } from '@/features/ai/hooks/useAssetAnalysisResult'
import { useCreateAssetAnalysis } from '@/features/ai/hooks/useCreateAssetAnalysis'
import { useCreateIntegralAnalysis } from '@/features/ai/hooks/useCreateIntegralAnalysis'
import { useCreateRecommendation } from '@/features/ai/hooks/useCreateRecommendation'
import { useCreateSentimentAnalysis } from '@/features/ai/hooks/useCreateSentimentAnalysis'
import { useIntegralAnalysisRequest } from '@/features/ai/hooks/useIntegralAnalysisRequest'
import { useIntegralAnalysisResult } from '@/features/ai/hooks/useIntegralAnalysisResult'
import { useRecommendationRequest } from '@/features/ai/hooks/useRecommendationRequest'
import { useRecommendationResult } from '@/features/ai/hooks/useRecommendationResult'
import { useSentimentAnalysisRequest } from '@/features/ai/hooks/useSentimentAnalysisRequest'
import { useSentimentAnalysisResult } from '@/features/ai/hooks/useSentimentAnalysisResult'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useAssets } from '@/features/market/hooks/useAssets'
import { useAssetNews } from '@/features/news/hooks/useAssetNews'
import { usePortfolios } from '@/features/portfolio/hooks/usePortfolios'

import '@/styles/ai.css'

type AiAnalysisMode = 'prediction' | 'sentiment' | 'recommendation' | 'integral'

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

export function AiAnalysisPage() {
  const { hasPermission } = useAuth()

  const canReadAnalysis = hasPermission('analisis.leer')
  const canReadAssets = hasPermission('activos.leer')
  const canRequestAnalysis = hasPermission('analisis.solicitar')
  const canReadNews = hasPermission('noticias.leer')
  const canReadPortfolios = hasPermission('portafolios.leer')

  const [analysisMode, setAnalysisMode] = useState<AiAnalysisMode>('prediction')

  const [predictionRequestId, setPredictionRequestId] = useState<string | null>(null)
  const [sentimentRequestId, setSentimentRequestId] = useState<string | null>(null)
  const [sentimentAssetId, setSentimentAssetId] = useState('')

  const [recommendationPredictionRequestId, setRecommendationPredictionRequestId] = useState<
    string | null
  >(null)
  const [recommendationRequestId, setRecommendationRequestId] = useState<string | null>(null)
  const [recommendationInput, setRecommendationInput] =
    useState<RecommendationFormSubmission | null>(null)

  const [integralInput, setIntegralInput] = useState<IntegralAnalysisFormSubmission | null>(null)
  const [integralAssetId, setIntegralAssetId] = useState('')
  const [integralPredictionRequestId, setIntegralPredictionRequestId] = useState<string | null>(
    null,
  )
  const [integralSentimentRequestId, setIntegralSentimentRequestId] = useState<string | null>(null)
  const [integralRequestId, setIntegralRequestId] = useState<string | null>(null)

  const recommendationCreationStartedRef = useRef(false)
  const integralSentimentCreationStartedRef = useRef(false)
  const integralCreationStartedRef = useRef(false)

  const createRecommendationPrediction = useCreateAssetAnalysis()
  const createRecommendation = useCreateRecommendation()

  const createIntegralPrediction = useCreateAssetAnalysis()
  const createIntegralSentiment = useCreateSentimentAnalysis()
  const createIntegral = useCreateIntegralAnalysis()

  const assetsQuery = useAssets(
    {
      status: 'ACTIVO',
      limit: 100,
      offset: 0,
    },
    canReadAnalysis && canReadAssets,
  )

  const portfoliosQuery = usePortfolios(
    {},
    canReadAnalysis && canReadPortfolios && analysisMode === 'recommendation',
  )

  const predictionRequestQuery = useAssetAnalysisRequest(
    predictionRequestId,
    canReadAnalysis && analysisMode === 'prediction',
  )

  const predictionRequestStatus = predictionRequestQuery.data?.status

  const predictionResultQuery = useAssetAnalysisResult(
    predictionRequestId,
    canReadAnalysis && analysisMode === 'prediction' && predictionRequestStatus === 'COMPLETADA',
  )

  const sentimentRequestQuery = useSentimentAnalysisRequest(
    sentimentRequestId,
    canReadAnalysis && analysisMode === 'sentiment',
  )

  const sentimentRequestStatus = sentimentRequestQuery.data?.status

  const sentimentResultQuery = useSentimentAnalysisResult(
    sentimentRequestId,
    canReadAnalysis && analysisMode === 'sentiment' && sentimentRequestStatus === 'COMPLETADA',
  )

  const recommendationPredictionQuery = useAssetAnalysisRequest(
    recommendationPredictionRequestId,
    canReadAnalysis && analysisMode === 'recommendation',
  )

  const recommendationPredictionStatus = recommendationPredictionQuery.data?.status

  const recommendationRequestQuery = useRecommendationRequest(
    recommendationRequestId,
    canReadAnalysis && analysisMode === 'recommendation',
  )

  const recommendationRequestStatus = recommendationRequestQuery.data?.status

  const recommendationResultQuery = useRecommendationResult(
    recommendationRequestId,
    canReadAnalysis &&
      analysisMode === 'recommendation' &&
      recommendationRequestStatus === 'COMPLETADA',
  )

  const integralPredictionQuery = useAssetAnalysisRequest(
    integralPredictionRequestId,
    canReadAnalysis && analysisMode === 'integral',
  )

  const integralPredictionStatus = integralPredictionQuery.data?.status

  const integralSentimentQuery = useSentimentAnalysisRequest(
    integralSentimentRequestId,
    canReadAnalysis && analysisMode === 'integral',
  )

  const integralSentimentStatus = integralSentimentQuery.data?.status

  const integralRequestQuery = useIntegralAnalysisRequest(
    integralRequestId,
    canReadAnalysis && analysisMode === 'integral',
  )

  const integralRequestStatus = integralRequestQuery.data?.status

  const integralResultQuery = useIntegralAnalysisResult(
    integralRequestId,
    canReadAnalysis && analysisMode === 'integral' && integralRequestStatus === 'COMPLETADA',
  )

  const activeNewsAssetId =
    analysisMode === 'sentiment'
      ? sentimentAssetId
      : analysisMode === 'integral'
        ? integralAssetId
        : ''

  const newsQuery = useAssetNews(
    activeNewsAssetId || null,
    {
      limit: 100,
      offset: 0,
    },
    canReadNews && (analysisMode === 'sentiment' || analysisMode === 'integral'),
  )

  const assets = useMemo(() => assetsQuery.data?.items ?? [], [assetsQuery.data?.items])

  const portfolios = useMemo(
    () => (portfoliosQuery.data?.items ?? []).filter((portfolio) => portfolio.estado === 'ACTIVO'),
    [portfoliosQuery.data?.items],
  )

  const news = useMemo(() => newsQuery.data?.items ?? [], [newsQuery.data?.items])

  const selectedPredictionAsset = useMemo(() => {
    const assetId = predictionResultQuery.data?.asset_id

    if (!assetId) {
      return undefined
    }

    return assets.find((asset) => asset.id === assetId)
  }, [assets, predictionResultQuery.data?.asset_id])

  const selectedSentimentAsset = useMemo(() => {
    const assetId = sentimentResultQuery.data?.asset_id

    if (!assetId) {
      return undefined
    }

    return assets.find((asset) => asset.id === assetId)
  }, [assets, sentimentResultQuery.data?.asset_id])

  const selectedSentimentNews = useMemo(() => {
    const newsReferenceId = sentimentResultQuery.data?.news_reference_id

    if (!newsReferenceId) {
      return undefined
    }

    return news.find((item) => item.reference_id === newsReferenceId)
  }, [news, sentimentResultQuery.data?.news_reference_id])

  const selectedRecommendationAsset = useMemo(() => {
    const assetId = recommendationResultQuery.data?.asset_id ?? recommendationInput?.asset_id

    if (!assetId) {
      return undefined
    }

    return assets.find((asset) => asset.id === assetId)
  }, [assets, recommendationInput?.asset_id, recommendationResultQuery.data?.asset_id])

  const selectedIntegralAsset = useMemo(() => {
    const assetId = integralResultQuery.data?.asset_id ?? integralInput?.asset_id

    if (!assetId) {
      return undefined
    }

    return assets.find((asset) => asset.id === assetId)
  }, [assets, integralInput?.asset_id, integralResultQuery.data?.asset_id])

  useEffect(() => {
    if (
      analysisMode !== 'recommendation' ||
      recommendationPredictionStatus !== 'COMPLETADA' ||
      !recommendationPredictionRequestId ||
      !recommendationInput ||
      recommendationRequestId ||
      recommendationCreationStartedRef.current
    ) {
      return
    }

    recommendationCreationStartedRef.current = true

    void createRecommendation
      .mutateAsync({
        asset_id: recommendationInput.asset_id,
        prediction_request_id: recommendationPredictionRequestId,
        portfolio_id: recommendationInput.portfolio_id,
        horizon: recommendationInput.horizon,
        reference_date: recommendationInput.reference_date,
      })
      .then((request) => {
        setRecommendationRequestId(request.id)
      })
      .catch(() => {
        recommendationCreationStartedRef.current = false
      })
  }, [
    analysisMode,
    createRecommendation,
    recommendationInput,
    recommendationPredictionRequestId,
    recommendationPredictionStatus,
    recommendationRequestId,
  ])

  useEffect(() => {
    if (
      analysisMode !== 'integral' ||
      integralPredictionStatus !== 'COMPLETADA' ||
      !integralPredictionRequestId ||
      !integralInput ||
      !integralInput.news_reference_id ||
      integralSentimentRequestId ||
      integralSentimentCreationStartedRef.current
    ) {
      return
    }

    integralSentimentCreationStartedRef.current = true

    const sentimentRequest: SentimentAnalysisRequestCreate = {
      asset_id: integralInput.asset_id,
      news_reference_id: integralInput.news_reference_id,
      reference_date: integralInput.reference_date,
    }

    void createIntegralSentiment
      .mutateAsync(sentimentRequest)
      .then((request) => {
        setIntegralSentimentRequestId(request.id)
      })
      .catch(() => {
        integralSentimentCreationStartedRef.current = false
      })
  }, [
    analysisMode,
    createIntegralSentiment,
    integralInput,
    integralPredictionRequestId,
    integralPredictionStatus,
    integralSentimentRequestId,
  ])

  useEffect(() => {
    if (
      analysisMode !== 'integral' ||
      integralPredictionStatus !== 'COMPLETADA' ||
      !integralPredictionRequestId ||
      !integralInput ||
      integralRequestId ||
      integralCreationStartedRef.current
    ) {
      return
    }

    const requiresSentiment = integralInput.news_reference_id !== null

    if (requiresSentiment && integralSentimentStatus !== 'COMPLETADA') {
      return
    }

    integralCreationStartedRef.current = true

    void createIntegral
      .mutateAsync({
        asset_id: integralInput.asset_id,
        prediction_request_id: integralPredictionRequestId,
        sentiment_request_ids: integralSentimentRequestId ? [integralSentimentRequestId] : [],
        horizon: integralInput.horizon,
        reference_date: integralInput.reference_date,
      })
      .then((request) => {
        setIntegralRequestId(request.id)
      })
      .catch(() => {
        integralCreationStartedRef.current = false
      })
  }, [
    analysisMode,
    createIntegral,
    integralInput,
    integralPredictionRequestId,
    integralPredictionStatus,
    integralRequestId,
    integralSentimentRequestId,
    integralSentimentStatus,
  ])

  if (!canReadAnalysis) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar análisis inteligentes."
      />
    )
  }

  function handlePredictionCreated(request: AnalysisRequestResponse) {
    setPredictionRequestId(request.id)
  }

  function handleSentimentCreated(request: AnalysisRequestResponse) {
    setSentimentRequestId(request.id)
  }

  async function handleRecommendationSubmit(data: RecommendationFormSubmission) {
    setRecommendationInput(data)
    setRecommendationPredictionRequestId(null)
    setRecommendationRequestId(null)
    recommendationCreationStartedRef.current = false

    createRecommendation.reset()

    const predictionRequest: AssetAnalysisRequestCreate = {
      asset_id: data.asset_id,
      horizon: data.horizon,
      reference_date: data.reference_date,
    }

    const request = await createRecommendationPrediction.mutateAsync(predictionRequest)

    setRecommendationPredictionRequestId(request.id)
  }

  async function handleIntegralSubmit(data: IntegralAnalysisFormSubmission) {
    setIntegralInput(data)
    setIntegralPredictionRequestId(null)
    setIntegralSentimentRequestId(null)
    setIntegralRequestId(null)

    integralSentimentCreationStartedRef.current = false
    integralCreationStartedRef.current = false

    createIntegralPrediction.reset()
    createIntegralSentiment.reset()
    createIntegral.reset()

    const predictionRequest: AssetAnalysisRequestCreate = {
      asset_id: data.asset_id,
      horizon: data.horizon,
      reference_date: data.reference_date,
    }

    const request = await createIntegralPrediction.mutateAsync(predictionRequest)

    setIntegralPredictionRequestId(request.id)
  }

  function resetRecommendation() {
    setRecommendationPredictionRequestId(null)
    setRecommendationRequestId(null)
    setRecommendationInput(null)
    recommendationCreationStartedRef.current = false

    createRecommendationPrediction.reset()
    createRecommendation.reset()
  }

  function resetIntegral() {
    setIntegralPredictionRequestId(null)
    setIntegralSentimentRequestId(null)
    setIntegralRequestId(null)
    setIntegralInput(null)

    integralSentimentCreationStartedRef.current = false
    integralCreationStartedRef.current = false

    createIntegralPrediction.reset()
    createIntegralSentiment.reset()
    createIntegral.reset()
  }

  function handleNewAnalysis() {
    if (analysisMode === 'prediction') {
      setPredictionRequestId(null)
      return
    }

    if (analysisMode === 'sentiment') {
      setSentimentRequestId(null)
      return
    }

    if (analysisMode === 'recommendation') {
      resetRecommendation()
      return
    }

    resetIntegral()
  }

  function handleModeChange(mode: AiAnalysisMode) {
    setAnalysisMode(mode)
  }

  const recommendationStarted =
    recommendationPredictionRequestId !== null ||
    recommendationRequestId !== null ||
    createRecommendationPrediction.isPending

  const integralStarted =
    integralPredictionRequestId !== null ||
    integralSentimentRequestId !== null ||
    integralRequestId !== null ||
    createIntegralPrediction.isPending

  const integralPredictionFailed =
    integralPredictionQuery.data?.status === 'FALLIDA' ||
    integralPredictionQuery.data?.status === 'CANCELADA'

  const integralSentimentFailed =
    integralSentimentQuery.data?.status === 'FALLIDA' ||
    integralSentimentQuery.data?.status === 'CANCELADA'

  const recommendationPredictionFailed =
    recommendationPredictionQuery.data?.status === 'FALLIDA' ||
    recommendationPredictionQuery.data?.status === 'CANCELADA'

  const activeRequestId =
    analysisMode === 'prediction'
      ? predictionRequestId
      : analysisMode === 'sentiment'
        ? sentimentRequestId
        : analysisMode === 'recommendation'
          ? recommendationStarted
            ? recommendationPredictionRequestId
            : null
          : integralStarted
            ? integralPredictionRequestId
            : null

  const activeRequestQuery =
    analysisMode === 'prediction'
      ? predictionRequestQuery
      : analysisMode === 'sentiment'
        ? sentimentRequestQuery
        : recommendationRequestId
          ? recommendationRequestQuery
          : recommendationPredictionQuery

  const activeRequestStatus = activeRequestQuery.data?.status

  return (
    <section className="ai-page">
      <header className="ai-page__header">
        <div>
          <p className="app__eyebrow">Inteligencia artificial</p>
          <h1>Análisis inteligente</h1>
          <p className="app__description">
            Explora predicciones, sentimiento, recomendaciones y análisis integrales utilizando las
            capacidades de AlphaInvest AI.
          </p>
        </div>

        {activeRequestId ? (
          <button className="button button--secondary" type="button" onClick={handleNewAnalysis}>
            Nuevo análisis
          </button>
        ) : null}
      </header>

      <nav className="ai-mode-tabs" aria-label="Tipos de análisis">
        <button
          className={`ai-mode-tabs__button ${
            analysisMode === 'prediction' ? 'ai-mode-tabs__button--active' : ''
          }`}
          type="button"
          aria-pressed={analysisMode === 'prediction'}
          onClick={() => {
            handleModeChange('prediction')
          }}
        >
          Predicción
        </button>

        <button
          className={`ai-mode-tabs__button ${
            analysisMode === 'sentiment' ? 'ai-mode-tabs__button--active' : ''
          }`}
          type="button"
          aria-pressed={analysisMode === 'sentiment'}
          onClick={() => {
            handleModeChange('sentiment')
          }}
        >
          Sentimiento
        </button>

        <button
          className={`ai-mode-tabs__button ${
            analysisMode === 'recommendation' ? 'ai-mode-tabs__button--active' : ''
          }`}
          type="button"
          aria-pressed={analysisMode === 'recommendation'}
          onClick={() => {
            handleModeChange('recommendation')
          }}
        >
          Recomendación
        </button>

        <button
          className={`ai-mode-tabs__button ${
            analysisMode === 'integral' ? 'ai-mode-tabs__button--active' : ''
          }`}
          type="button"
          aria-pressed={analysisMode === 'integral'}
          onClick={() => {
            handleModeChange('integral')
          }}
        >
          Integral
        </button>
      </nav>

      {assetsQuery.isPending ? (
        <PageLoadingState message="Cargando activos disponibles..." />
      ) : assetsQuery.isError ? (
        <PageErrorState
          title="No fue posible cargar los activos"
          message={assetsQuery.error.message}
          onRetry={() => {
            void assetsQuery.refetch()
          }}
        />
      ) : analysisMode === 'integral' ? (
        !integralStarted ? (
          !canRequestAnalysis ? (
            <PageErrorState
              title="Solicitud de análisis restringida"
              message="Puedes consultar análisis, pero tu usuario no cuenta con permiso para solicitar nuevos análisis integrales."
            />
          ) : (
            <IntegralAnalysisForm
              assets={assets}
              news={news}
              selectedAssetId={integralAssetId}
              newsLoading={newsQuery.isPending && Boolean(integralAssetId)}
              newsError={
                !canReadNews
                  ? 'Tu usuario no cuenta con permiso para consultar noticias. El análisis integral continuará sin sentimiento.'
                  : newsQuery.isError
                    ? newsQuery.error.message
                    : undefined
              }
              onAssetChange={setIntegralAssetId}
              onRetryNews={() => {
                void newsQuery.refetch()
              }}
              onSubmit={handleIntegralSubmit}
            />
          )
        ) : createIntegralPrediction.isError && integralPredictionRequestId === null ? (
          <PageErrorState
            title="No fue posible iniciar el análisis integral"
            message={createIntegralPrediction.error.message}
            onRetry={resetIntegral}
          />
        ) : integralPredictionRequestId === null ? (
          <PageLoadingState message="Registrando la predicción necesaria..." />
        ) : integralPredictionQuery.isPending ? (
          <PageLoadingState message="Consultando la predicción necesaria..." />
        ) : integralPredictionQuery.isError ? (
          <PageErrorState
            title="No fue posible consultar la predicción"
            message={integralPredictionQuery.error.message}
            onRetry={() => {
              void integralPredictionQuery.refetch()
            }}
          />
        ) : integralPredictionFailed ? (
          <PageErrorState
            title="La predicción necesaria no pudo completarse"
            message={
              integralPredictionQuery.data.error_message ??
              'No fue posible generar la predicción requerida para el análisis integral.'
            }
          />
        ) : integralPredictionStatus !== 'COMPLETADA' ? (
          <section className="ai-request">
            <header className="ai-request__header">
              <div>
                <p className="app__eyebrow">Paso 1</p>
                <h2>Generando predicción</h2>
              </div>

              <span
                className={`ai-request-status ai-request-status--${integralPredictionQuery.data.status.toLowerCase()}`}
              >
                {formatRequestStatus(integralPredictionQuery.data.status)}
              </span>
            </header>

            <AiRequestProgress
              status={integralPredictionQuery.data.status}
              progressPercentage={integralPredictionQuery.data.progress_percentage}
              executingTitle="Analizando el activo"
              executingDescription="Generando la predicción base necesaria para el análisis integral."
            />
          </section>
        ) : integralInput?.news_reference_id && !integralSentimentRequestId ? (
          createIntegralSentiment.isError ? (
            <PageErrorState
              title="No fue posible iniciar el análisis de sentimiento"
              message={createIntegralSentiment.error.message}
              onRetry={resetIntegral}
            />
          ) : (
            <PageLoadingState message="Predicción completada. Iniciando análisis de sentimiento..." />
          )
        ) : integralInput?.news_reference_id &&
          integralSentimentRequestId &&
          integralSentimentQuery.isPending ? (
          <PageLoadingState message="Consultando el análisis de sentimiento..." />
        ) : integralInput?.news_reference_id &&
          integralSentimentRequestId &&
          integralSentimentQuery.isError ? (
          <PageErrorState
            title="No fue posible consultar el análisis de sentimiento"
            message={integralSentimentQuery.error.message}
            onRetry={() => {
              void integralSentimentQuery.refetch()
            }}
          />
        ) : integralInput?.news_reference_id && integralSentimentFailed ? (
          <PageErrorState
            title="El análisis de sentimiento no pudo completarse"
            message={
              integralSentimentQuery.data?.error_message ??
              'No fue posible generar el sentimiento requerido para el análisis integral.'
            }
          />
        ) : integralInput?.news_reference_id && integralSentimentStatus !== 'COMPLETADA' ? (
          <section className="ai-request">
            <header className="ai-request__header">
              <div>
                <p className="app__eyebrow">Paso 2</p>
                <h2>Analizando sentimiento</h2>
              </div>

              {integralSentimentQuery.data ? (
                <span
                  className={`ai-request-status ai-request-status--${integralSentimentQuery.data.status.toLowerCase()}`}
                >
                  {formatRequestStatus(integralSentimentQuery.data.status)}
                </span>
              ) : null}
            </header>

            {integralSentimentQuery.data ? (
              <AiRequestProgress
                status={integralSentimentQuery.data.status}
                progressPercentage={integralSentimentQuery.data.progress_percentage}
                executingTitle="Evaluando la noticia"
                executingDescription="El modelo está incorporando el sentimiento como evidencia del análisis integral."
              />
            ) : (
              <PageLoadingState message="Consultando el análisis de sentimiento..." />
            )}
          </section>
        ) : !integralRequestId ? (
          createIntegral.isError ? (
            <PageErrorState
              title="No fue posible crear el análisis integral"
              message={createIntegral.error.message}
              onRetry={resetIntegral}
            />
          ) : (
            <PageLoadingState message="Preparando el análisis integral..." />
          )
        ) : integralRequestQuery.isPending ? (
          <PageLoadingState message="Consultando estado del análisis integral..." />
        ) : integralRequestQuery.isError ? (
          <PageErrorState
            title="No fue posible consultar el análisis integral"
            message={integralRequestQuery.error.message}
            onRetry={() => {
              void integralRequestQuery.refetch()
            }}
          />
        ) : integralRequestQuery.data.status === 'PENDIENTE' ||
          integralRequestQuery.data.status === 'EJECUTANDO' ? (
          <section className="ai-request">
            <header className="ai-request__header">
              <div>
                <p className="app__eyebrow">Análisis integral</p>
                <h2>Integrando señales</h2>
              </div>

              <span
                className={`ai-request-status ai-request-status--${integralRequestQuery.data.status.toLowerCase()}`}
              >
                {formatRequestStatus(integralRequestQuery.data.status)}
              </span>
            </header>

            <AiRequestProgress
              status={integralRequestQuery.data.status}
              progressPercentage={integralRequestQuery.data.progress_percentage}
              executingTitle="Construyendo recomendación integral"
              executingDescription={`AlphaInvest AI está integrando la predicción, el contexto disponible${
                integralInput?.news_reference_id ? ' y el análisis de sentimiento' : ''
              }.`}
            />
          </section>
        ) : integralRequestQuery.data.status === 'FALLIDA' ? (
          <PageErrorState
            title="El análisis integral no pudo completarse"
            message={
              integralRequestQuery.data.error_message ??
              'El motor de inteligencia artificial reportó un error durante el análisis integral.'
            }
          />
        ) : integralRequestQuery.data.status === 'CANCELADA' ? (
          <PageErrorState
            title="Análisis integral cancelado"
            message="La solicitud fue cancelada antes de generar un resultado."
          />
        ) : integralResultQuery.isPending ? (
          <PageLoadingState message="Cargando resultado del análisis integral..." />
        ) : integralResultQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar el resultado integral"
            message={integralResultQuery.error.message}
            onRetry={() => {
              void integralResultQuery.refetch()
            }}
          />
        ) : (
          <RecommendationResult result={integralResultQuery.data} asset={selectedIntegralAsset} />
        )
      ) : analysisMode === 'recommendation' ? (
        !recommendationStarted ? (
          canRequestAnalysis ? (
            <RecommendationForm
              assets={assets}
              portfolios={portfolios}
              portfoliosLoading={canReadPortfolios && portfoliosQuery.isPending}
              portfoliosError={
                canReadPortfolios && portfoliosQuery.isError
                  ? portfoliosQuery.error.message
                  : undefined
              }
              onRetryPortfolios={() => {
                void portfoliosQuery.refetch()
              }}
              onSubmit={handleRecommendationSubmit}
            />
          ) : (
            <PageErrorState
              title="Solicitud de análisis restringida"
              message="Puedes consultar análisis, pero tu usuario no cuenta con permiso para solicitar nuevas recomendaciones."
            />
          )
        ) : createRecommendationPrediction.isError && recommendationPredictionRequestId === null ? (
          <PageErrorState
            title="No fue posible iniciar la recomendación"
            message={createRecommendationPrediction.error.message}
            onRetry={resetRecommendation}
          />
        ) : recommendationPredictionRequestId === null ? (
          <PageLoadingState message="Registrando la predicción necesaria..." />
        ) : recommendationPredictionQuery.isPending ? (
          <PageLoadingState message="Consultando la predicción necesaria..." />
        ) : recommendationPredictionQuery.isError ? (
          <PageErrorState
            title="No fue posible consultar la predicción"
            message={recommendationPredictionQuery.error.message}
            onRetry={() => {
              void recommendationPredictionQuery.refetch()
            }}
          />
        ) : recommendationPredictionFailed ? (
          <PageErrorState
            title="La predicción necesaria no pudo completarse"
            message={
              recommendationPredictionQuery.data.error_message ??
              'No fue posible generar la predicción requerida para construir la recomendación.'
            }
          />
        ) : recommendationPredictionStatus !== 'COMPLETADA' ? (
          <section className="ai-request">
            <header className="ai-request__header">
              <div>
                <p className="app__eyebrow">Paso 1 de 2</p>
                <h2>Generando predicción</h2>
              </div>

              <span
                className={`ai-request-status ai-request-status--${recommendationPredictionQuery.data.status.toLowerCase()}`}
              >
                {formatRequestStatus(recommendationPredictionQuery.data.status)}
              </span>
            </header>

            <AiRequestProgress
              status={recommendationPredictionQuery.data.status}
              progressPercentage={recommendationPredictionQuery.data.progress_percentage}
              executingTitle="Analizando el activo"
              executingDescription="AlphaInvest AI está generando la predicción que servirá como base para la recomendación."
            />
          </section>
        ) : !recommendationRequestId ? (
          createRecommendation.isError ? (
            <PageErrorState
              title="No fue posible crear la recomendación"
              message={createRecommendation.error.message}
              onRetry={resetRecommendation}
            />
          ) : (
            <PageLoadingState message="Predicción completada. Generando solicitud de recomendación..." />
          )
        ) : recommendationRequestQuery.isPending ? (
          <PageLoadingState message="Consultando estado de la recomendación..." />
        ) : recommendationRequestQuery.isError ? (
          <PageErrorState
            title="No fue posible consultar la recomendación"
            message={recommendationRequestQuery.error.message}
            onRetry={() => {
              void recommendationRequestQuery.refetch()
            }}
          />
        ) : recommendationRequestQuery.data.status === 'PENDIENTE' ||
          recommendationRequestQuery.data.status === 'EJECUTANDO' ? (
          <section className="ai-request">
            <header className="ai-request__header">
              <div>
                <p className="app__eyebrow">Paso 2 de 2</p>
                <h2>Generando recomendación</h2>
              </div>

              <span
                className={`ai-request-status ai-request-status--${recommendationRequestQuery.data.status.toLowerCase()}`}
              >
                {formatRequestStatus(recommendationRequestQuery.data.status)}
              </span>
            </header>

            <AiRequestProgress
              status={recommendationRequestQuery.data.status}
              progressPercentage={recommendationRequestQuery.data.progress_percentage}
              executingTitle="Evaluando señales"
              executingDescription="El motor está evaluando la predicción y el contexto disponible para construir una recomendación explicable."
            />
          </section>
        ) : recommendationRequestQuery.data.status === 'FALLIDA' ? (
          <PageErrorState
            title="La recomendación no pudo completarse"
            message={
              recommendationRequestQuery.data.error_message ??
              'El motor de recomendaciones reportó un error durante el procesamiento.'
            }
          />
        ) : recommendationRequestQuery.data.status === 'CANCELADA' ? (
          <PageErrorState
            title="Recomendación cancelada"
            message="La solicitud fue cancelada antes de generar un resultado."
          />
        ) : recommendationResultQuery.isPending ? (
          <PageLoadingState message="Cargando resultado de la recomendación..." />
        ) : recommendationResultQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar la recomendación"
            message={recommendationResultQuery.error.message}
            onRetry={() => {
              void recommendationResultQuery.refetch()
            }}
          />
        ) : (
          <RecommendationResult
            result={recommendationResultQuery.data}
            asset={selectedRecommendationAsset}
          />
        )
      ) : !activeRequestId ? (
        analysisMode === 'prediction' ? (
          canRequestAnalysis ? (
            <AssetAnalysisForm assets={assets} onCreated={handlePredictionCreated} />
          ) : (
            <PageErrorState
              title="Solicitud de análisis restringida"
              message="Puedes consultar análisis, pero tu usuario no cuenta con permiso para solicitar nuevos análisis."
            />
          )
        ) : !canReadNews ? (
          <PageErrorState
            title="Consulta de noticias restringida"
            message="Tu usuario no cuenta con permiso para consultar las noticias necesarias para realizar el análisis de sentimiento."
          />
        ) : canRequestAnalysis ? (
          <SentimentAnalysisForm
            assets={assets}
            news={news}
            selectedAssetId={sentimentAssetId}
            newsLoading={newsQuery.isPending && Boolean(sentimentAssetId)}
            newsError={newsQuery.isError ? newsQuery.error.message : undefined}
            onAssetChange={setSentimentAssetId}
            onRetryNews={() => {
              void newsQuery.refetch()
            }}
            onCreated={handleSentimentCreated}
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
              <h2>
                {analysisMode === 'prediction'
                  ? 'Procesamiento de la predicción'
                  : 'Procesamiento del sentimiento'}
              </h2>
            </div>

            {activeRequestStatus ? (
              <span
                className={`ai-request-status ai-request-status--${activeRequestStatus.toLowerCase()}`}
              >
                {formatRequestStatus(activeRequestStatus)}
              </span>
            ) : null}
          </header>

          {activeRequestQuery.isPending ? (
            <PageLoadingState message="Consultando estado del análisis..." />
          ) : activeRequestQuery.isError ? (
            <PageErrorState
              title="No fue posible consultar el análisis"
              message={activeRequestQuery.error.message}
              onRetry={() => {
                void activeRequestQuery.refetch()
              }}
            />
          ) : activeRequestQuery.data.status === 'PENDIENTE' ||
            activeRequestQuery.data.status === 'EJECUTANDO' ? (
            <AiRequestProgress
              status={activeRequestQuery.data.status}
              progressPercentage={activeRequestQuery.data.progress_percentage}
              pendingTitle="Análisis pendiente"
              pendingDescription="La solicitud está esperando ser procesada por el motor de inteligencia artificial."
              executingTitle="Analizando información"
              executingDescription={
                analysisMode === 'prediction'
                  ? 'Los modelos están procesando la información disponible para generar la predicción.'
                  : 'El modelo está procesando el contenido de la noticia para determinar su sentimiento.'
              }
            />
          ) : activeRequestQuery.data.status === 'FALLIDA' ? (
            <PageErrorState
              title="El análisis no pudo completarse"
              message={
                activeRequestQuery.data.error_message ??
                'El motor de inteligencia artificial reportó un error durante el procesamiento.'
              }
            />
          ) : activeRequestQuery.data.status === 'CANCELADA' ? (
            <PageErrorState
              title="Análisis cancelado"
              message="La solicitud fue cancelada antes de generar un resultado."
            />
          ) : analysisMode === 'prediction' ? (
            predictionResultQuery.isPending ? (
              <PageLoadingState message="Cargando resultado de la predicción..." />
            ) : predictionResultQuery.isError ? (
              <PageErrorState
                title="No fue posible cargar el resultado"
                message={predictionResultQuery.error.message}
                onRetry={() => {
                  void predictionResultQuery.refetch()
                }}
              />
            ) : (
              <AssetAnalysisResult
                result={predictionResultQuery.data}
                asset={selectedPredictionAsset}
              />
            )
          ) : sentimentResultQuery.isPending ? (
            <PageLoadingState message="Cargando resultado del análisis de sentimiento..." />
          ) : sentimentResultQuery.isError ? (
            <PageErrorState
              title="No fue posible cargar el resultado"
              message={sentimentResultQuery.error.message}
              onRetry={() => {
                void sentimentResultQuery.refetch()
              }}
            />
          ) : (
            <SentimentAnalysisResult
              result={sentimentResultQuery.data}
              asset={selectedSentimentAsset}
              news={selectedSentimentNews}
            />
          )}
        </section>
      )}
    </section>
  )
}
