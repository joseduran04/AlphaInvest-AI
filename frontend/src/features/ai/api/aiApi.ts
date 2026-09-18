import { apiClient } from '@/api/client'
import type {
  AnalysisRequestResponse,
  AssetAnalysisRequestCreate,
  AssetAnalysisResultResponse,
  IntegralAnalysisRequestCreate,
  RecommendationRequestCreate,
  RecommendationResultResponse,
  SentimentAnalysisRequestCreate,
  SentimentAnalysisResultResponse,
} from '@/api/types'

const AI_PATH = '/api/v1/ai'

export async function createAssetAnalysisRequest(
  data: AssetAnalysisRequestCreate,
): Promise<AnalysisRequestResponse> {
  const response = await apiClient.post<AnalysisRequestResponse>(
    `${AI_PATH}/analysis-requests`,
    data,
  )

  return response.data
}

export async function assetAnalysisRequest(requestId: string): Promise<AnalysisRequestResponse> {
  const response = await apiClient.get<AnalysisRequestResponse>(
    `${AI_PATH}/analysis-requests/${requestId}`,
  )

  return response.data
}

export async function assetAnalysisResultRequest(
  requestId: string,
): Promise<AssetAnalysisResultResponse> {
  const response = await apiClient.get<AssetAnalysisResultResponse>(
    `${AI_PATH}/analysis-requests/${requestId}/result`,
  )

  return response.data
}

export async function createSentimentAnalysisRequest(
  data: SentimentAnalysisRequestCreate,
): Promise<AnalysisRequestResponse> {
  const response = await apiClient.post<AnalysisRequestResponse>(
    `${AI_PATH}/sentiment-analysis-requests`,
    data,
  )

  return response.data
}

export async function sentimentAnalysisResultRequest(
  requestId: string,
): Promise<SentimentAnalysisResultResponse> {
  const response = await apiClient.get<SentimentAnalysisResultResponse>(
    `${AI_PATH}/sentiment-analysis-requests/${requestId}/result`,
  )

  return response.data
}

export async function createRecommendationRequest(
  data: RecommendationRequestCreate,
): Promise<AnalysisRequestResponse> {
  const response = await apiClient.post<AnalysisRequestResponse>(
    `${AI_PATH}/recommendation-requests`,
    data,
  )

  return response.data
}

export async function recommendationRequest(requestId: string): Promise<AnalysisRequestResponse> {
  const response = await apiClient.get<AnalysisRequestResponse>(
    `${AI_PATH}/recommendation-requests/${requestId}`,
  )

  return response.data
}

export async function recommendationResultRequest(
  requestId: string,
): Promise<RecommendationResultResponse> {
  const response = await apiClient.get<RecommendationResultResponse>(
    `${AI_PATH}/recommendation-requests/${requestId}/result`,
  )

  return response.data
}

export async function createIntegralAnalysisRequest(
  data: IntegralAnalysisRequestCreate,
): Promise<AnalysisRequestResponse> {
  const response = await apiClient.post<AnalysisRequestResponse>(
    `${AI_PATH}/integral-analysis-requests`,
    data,
  )

  return response.data
}

export async function integralAnalysisRequest(requestId: string): Promise<AnalysisRequestResponse> {
  const response = await apiClient.get<AnalysisRequestResponse>(
    `${AI_PATH}/integral-analysis-requests/${requestId}`,
  )

  return response.data
}

export async function integralAnalysisResultRequest(
  requestId: string,
): Promise<RecommendationResultResponse> {
  const response = await apiClient.get<RecommendationResultResponse>(
    `${AI_PATH}/integral-analysis-requests/${requestId}/result`,
  )

  return response.data
}
