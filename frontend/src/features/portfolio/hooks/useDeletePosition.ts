import { useMutation, useQueryClient } from '@tanstack/react-query'

import { deletePositionRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function useDeletePosition(portfolioId: string, positionId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => deletePositionRequest(portfolioId, positionId),

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
