import { useQuery } from '@tanstack/react-query'

import { sentimentAnalysisResultRequest } from '@/features/ai/api/aiApi'
import { aiQueryKeys } from '@/features/ai/hooks/aiQueryKeys'

export function useSentimentAnalysisResult(requestId: string | null, enabled = true) {
  return useQuery({
    queryKey: aiQueryKeys.sentimentAnalysisResult(requestId ?? 'none'),
    queryFn: () => {
      if (!requestId) {
        throw new Error('Se requiere una solicitud para consultar el resultado de sentimiento')
      }

      return sentimentAnalysisResultRequest(requestId)
    },
    enabled: enabled && requestId !== null,
  })
}
