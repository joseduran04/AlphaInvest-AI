import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { PositionCreateRequest } from '@/api/types'
import { createPositionRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function useCreatePosition(portfolioId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: PositionCreateRequest) => createPositionRequest(portfolioId, data),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: portfolioQueryKeys.positionsRoot(portfolioId),
        }),
        queryClient.invalidateQueries({
          queryKey: portfolioQueryKeys.summary(portfolioId),
        }),
        queryClient.invalidateQueries({
          queryKey: portfolioQueryKeys.allocationRoot(portfolioId),
        }),
      ])
    },
  })
}
