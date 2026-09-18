import { useQuery } from '@tanstack/react-query'

import type { AssetNewsListQuery } from '@/api/types'
import { assetNewsRequest } from '@/features/news/api/newsApi'
import { newsQueryKeys } from '@/features/news/hooks/newsQueryKeys'

export function useAssetNews(
  assetId: string | null,
  params: AssetNewsListQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: newsQueryKeys.assetNews(assetId ?? 'none', params),
    queryFn: () => {
      if (!assetId) {
        throw new Error('Se requiere un activo para consultar sus noticias')
      }

      return assetNewsRequest(assetId, params)
    },
    enabled: enabled && assetId !== null,
  })
}
