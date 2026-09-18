import { useMutation } from '@tanstack/react-query'

import type { SentimentAnalysisRequestCreate } from '@/api/types'
import { createSentimentAnalysisRequest } from '@/features/ai/api/aiApi'

export function useCreateSentimentAnalysis() {
  return useMutation({
    mutationFn: (data: SentimentAnalysisRequestCreate) => createSentimentAnalysisRequest(data),
  })
}
