import { useQuery } from '@tanstack/react-query'

import type { AnalysisRequestStatus } from '@/api/types'
import { integralAnalysisRequest } from '@/features/ai/api/aiApi'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'

const ACTIVE_INTEGRAL_STATUSES: ReadonlySet<AnalysisRequestStatus> = new Set([
  'PENDIENTE',
  'EJECUTANDO',
])

export function useIntegralAnalysisRequest(requestId: string | null, enabled = true) {
  return useQuery({
    queryKey: aiQueryKeys.integralAnalysisRequest(requestId ?? 'none'),
    queryFn: () => {
      if (!requestId) {
        throw new Error('Se requiere una solicitud para consultar el análisis integral')
      }

      return integralAnalysisRequest(requestId)
    },
    enabled: enabled && requestId !== null,
    refetchInterval: (query) => {
      const status = query.state.data?.status

      if (!status || !ACTIVE_INTEGRAL_STATUSES.has(status)) {
        return false
      }

      return 2_000
    },
  })
}
