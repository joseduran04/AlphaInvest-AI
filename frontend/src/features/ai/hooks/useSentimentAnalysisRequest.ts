import { useQuery } from '@tanstack/react-query'

import type { AnalysisRequestStatus } from '@/api/types'
import { assetAnalysisRequest } from '@/features/ai/api/aiApi'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'

const ACTIVE_ANALYSIS_STATUSES: ReadonlySet<AnalysisRequestStatus> = new Set([
  'PENDIENTE',
  'EJECUTANDO',
])

export function useSentimentAnalysisRequest(requestId: string | null, enabled = true) {
  return useQuery({
    queryKey: aiQueryKeys.sentimentAnalysisRequest(requestId ?? 'none'),
    queryFn: () => {
      if (!requestId) {
        throw new Error('Se requiere una solicitud para consultar el análisis de sentimiento')
      }

      return assetAnalysisRequest(requestId)
    },
    enabled: enabled && requestId !== null,
    refetchInterval: (query) => {
      const status = query.state.data?.status

      if (!status || !ACTIVE_ANALYSIS_STATUSES.has(status)) {
        return false
      }

      return 2_000
    },
  })
}
