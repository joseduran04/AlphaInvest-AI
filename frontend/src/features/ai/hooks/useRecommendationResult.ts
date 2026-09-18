import { useQuery } from '@tanstack/react-query'

import { recommendationResultRequest } from '@/features/ai/api/aiApi'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'

export function useRecommendationResult(requestId: string | null, enabled = true) {
  return useQuery({
    queryKey: aiQueryKeys.recommendationResult(requestId ?? 'none'),
    queryFn: () => {
      if (!requestId) {
        throw new Error('Se requiere una solicitud para consultar el resultado de la recomendación')
      }

      return recommendationResultRequest(requestId)
    },
    enabled: enabled && requestId !== null,
  })
}
