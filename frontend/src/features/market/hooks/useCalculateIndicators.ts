import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { IndicatorCalculationRequest } from '@/api/types'
import { calculateAssetIndicatorsRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useCalculateIndicators(assetId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: IndicatorCalculationRequest) =>
      calculateAssetIndicatorsRequest(assetId, data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: marketQueryKeys.indicatorsRoot(assetId),
      })
    },
  })
}
