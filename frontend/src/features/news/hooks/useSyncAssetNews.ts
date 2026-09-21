import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { AssetNewsSynchronizationQuery } from '@/api/types'
import { synchronizeAssetNewsRequest } from '@/features/news/api/newsApi'
import { newsQueryKeys } from '@/features/news/hooks/newsQueryKeys'

export function useSyncAssetNews(assetId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (params: AssetNewsSynchronizationQuery = {}) =>
      synchronizeAssetNewsRequest(assetId, params),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: newsQueryKeys.assetNewsRoot(),
      })
    },
  })
}
