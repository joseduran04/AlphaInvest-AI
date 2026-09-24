import { useQuery } from '@tanstack/react-query'

import { assetSentimentSummaryRequest } from '@/features/ai/api/aiApi'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'

export function useAssetSentimentSummary(assetId: string | null, enabled = true) {
  return useQuery({
    queryKey: aiQueryKeys.assetSentimentSummary(assetId ?? 'none'),
    queryFn: () => {
      if (!assetId) {
        throw new Error('Se requiere un activo para consultar el sentimiento')
      }

      return assetSentimentSummaryRequest(assetId)
    },
    enabled: enabled && assetId !== null,
  })
}
