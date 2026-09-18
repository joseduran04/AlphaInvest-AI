import { apiClient } from '@/api/client'
import type { AssetNewsListQuery, NewsListResponse } from '@/api/types'

const NEWS_PATH = '/api/v1/news'

export async function assetNewsRequest(
  assetId: string,
  params: AssetNewsListQuery = {},
): Promise<NewsListResponse> {
  const response = await apiClient.get<NewsListResponse>(`${NEWS_PATH}/assets/${assetId}`, {
    params,
  })

  return response.data
}
