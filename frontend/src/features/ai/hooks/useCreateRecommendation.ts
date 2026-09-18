import { useMutation } from '@tanstack/react-query'

import type { RecommendationRequestCreate } from '@/api/types'
import { createRecommendationRequest } from '@/features/ai/api/aiApi'

export function useCreateRecommendation() {
  return useMutation({
    mutationFn: (data: RecommendationRequestCreate) => createRecommendationRequest(data),
  })
}
