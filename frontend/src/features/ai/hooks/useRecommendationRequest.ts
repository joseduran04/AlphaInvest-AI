import { useQuery } from '@tanstack/react-query'

import type { AnalysisRequestStatus } from '@/api/types'
import { recommendationRequest } from '@/features/ai/api/aiApi'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'

const ACTIVE_RECOMMENDATION_STATUSES: ReadonlySet<AnalysisRequestStatus> = new Set([
  'PENDIENTE',
  'EJECUTANDO',
])

export function useRecommendationRequest(requestId: string | null, enabled = true) {
  return useQuery({
    queryKey: aiQueryKeys.recommendationRequest(requestId ?? 'none'),
    queryFn: () => {
      if (!requestId) {
        throw new Error('Se requiere una solicitud para consultar la recomendación')
      }

      return recommendationRequest(requestId)
    },
    enabled: enabled && requestId !== null,
    refetchInterval: (query) => {
      const status = query.state.data?.status

      if (!status || !ACTIVE_RECOMMENDATION_STATUSES.has(status)) {
        return false
      }

      return 2_000
    },
  })
}
