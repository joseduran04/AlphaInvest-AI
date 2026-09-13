import { useMutation, useQueryClient } from '@tanstack/react-query'

import { synchronizeAssetPricesRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useSyncAssetPrices(assetId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => synchronizeAssetPricesRequest(assetId),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: marketQueryKeys.prices(assetId),
      })
    },
  })
}
