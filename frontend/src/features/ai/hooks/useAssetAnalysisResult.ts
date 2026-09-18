import { useQuery } from '@tanstack/react-query'

import { assetAnalysisResultRequest } from '@/features/ai/api/aiApi'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'

export function useAssetAnalysisResult(requestId: string | null, enabled = true) {
  return useQuery({
    queryKey: aiQueryKeys.assetAnalysisResult(requestId ?? 'none'),
    queryFn: () => {
      if (!requestId) {
        throw new Error('Se requiere una solicitud para consultar el resultado del análisis')
      }

      return assetAnalysisResultRequest(requestId)
    },
    enabled: enabled && requestId !== null,
  })
}
