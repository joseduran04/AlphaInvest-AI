import { apiClient } from '@/api/client'
import type {
  AssetNewsListQuery,
  AssetNewsSynchronizationQuery,
  NewsListResponse,
  NewsSynchronizationResponse,
} from '@/api/types'

const NEWS_PATH = '/api/v1/news'
const NEWS_SYNCHRONIZATION_TIMEOUT_MS = 60_000

export async function assetNewsRequest(
  assetId: string,
  params: AssetNewsListQuery = {},
): Promise<NewsListResponse> {
  const response = await apiClient.get<NewsListResponse>(`${NEWS_PATH}/assets/${assetId}`, {
    params,
  })

  return response.data
}

export async function synchronizeAssetNewsRequest(
  assetId: string,
  params: AssetNewsSynchronizationQuery = {},
): Promise<NewsSynchronizationResponse> {
  const response = await apiClient.post<NewsSynchronizationResponse>(
    `${NEWS_PATH}/assets/${assetId}/sync`,
    undefined,
    {
      params,
      timeout: NEWS_SYNCHRONIZATION_TIMEOUT_MS,
    },
  )

  return response.data
}
