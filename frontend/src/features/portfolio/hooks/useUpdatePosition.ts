import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { PositionUpdateRequest } from '@/api/types'
import { updatePositionRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function useUpdatePosition(portfolioId: string, positionId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: PositionUpdateRequest) =>
      updatePositionRequest(portfolioId, positionId, data),

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
