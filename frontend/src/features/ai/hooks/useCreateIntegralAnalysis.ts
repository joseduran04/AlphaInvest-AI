import { useMutation } from '@tanstack/react-query'

import type { IntegralAnalysisRequestCreate } from '@/api/types'
import { createIntegralAnalysisRequest } from '@/features/ai/api/aiApi'

export function useCreateIntegralAnalysis() {
  return useMutation({
    mutationFn: (data: IntegralAnalysisRequestCreate) => createIntegralAnalysisRequest(data),
  })
}
