import { useMutation } from '@tanstack/react-query'

import type { AssetAnalysisRequestCreate } from '@/api/types'
import { createAssetAnalysisRequest } from '@/features/ai/api/aiApi'

export function useCreateAssetAnalysis() {
  return useMutation({
    mutationFn: (data: AssetAnalysisRequestCreate) => createAssetAnalysisRequest(data),
  })
}
