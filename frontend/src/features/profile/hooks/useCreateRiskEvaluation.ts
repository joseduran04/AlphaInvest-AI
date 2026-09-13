import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { CreateRiskEvaluationRequest } from '@/api/types'
import { createRiskEvaluationRequest } from '@/features/profile/api/profileApi'
import { profileQueryKeys } from '@/features/profile/hooks/profileQueryKeys'

export function useCreateRiskEvaluation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateRiskEvaluationRequest) => createRiskEvaluationRequest(data),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: profileQueryKeys.current(),
        }),
        queryClient.invalidateQueries({
          queryKey: profileQueryKeys.history(),
        }),
      ])
    },
  })
}
