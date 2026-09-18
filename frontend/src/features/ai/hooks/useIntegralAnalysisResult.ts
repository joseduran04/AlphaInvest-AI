import { useQuery } from '@tanstack/react-query'

import { integralAnalysisResultRequest } from '@/features/ai/api/aiApi'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'

export function useIntegralAnalysisResult(requestId: string | null, enabled = true) {
  return useQuery({
    queryKey: aiQueryKeys.integralAnalysisResult(requestId ?? 'none'),
    queryFn: () => {
      if (!requestId) {
        throw new Error(
          'Se requiere una solicitud para consultar el resultado del análisis integral',
        )
      }

      return integralAnalysisResultRequest(requestId)
    },
    enabled: enabled && requestId !== null,
  })
}
