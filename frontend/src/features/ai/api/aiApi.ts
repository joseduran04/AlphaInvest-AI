import { apiClient } from '@/api/client'
import type {
  AnalysisRequestResponse,
  AssetSentimentSummaryResponse,
  SentimentAnalysisRequestCreate,
  SentimentAnalysisResultResponse,
} from '@/api/types'

const AI_PATH = '/api/v1/ai'

export async function createSentimentAnalysisRequest(
  data: SentimentAnalysisRequestCreate,
): Promise<AnalysisRequestResponse> {
  const response = await apiClient.post<AnalysisRequestResponse>(
    `${AI_PATH}/sentiment-analysis-requests`,
    data,
  )

  return response.data
}

export async function sentimentAnalysisRequest(
  requestId: string,
): Promise<AnalysisRequestResponse> {
  const response = await apiClient.get<AnalysisRequestResponse>(
    `${AI_PATH}/analysis-requests/${requestId}`,
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

export async function assetSentimentSummaryRequest(
  assetId: string,
  limit = 20,
): Promise<AssetSentimentSummaryResponse> {
  const response = await apiClient.get<AssetSentimentSummaryResponse>(
    `${AI_PATH}/assets/${assetId}/sentiment-summary`,
    { params: { limit } },
  )

  return response.data
}
