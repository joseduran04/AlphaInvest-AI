import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { PortfolioValuationCreateRequest } from '@/api/types'
import { createPortfolioValuationRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function useCreatePortfolioValuation(portfolioId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: PortfolioValuationCreateRequest) =>
      createPortfolioValuationRequest(portfolioId, data),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: portfolioQueryKeys.valuationsRoot(portfolioId),
        }),
        queryClient.invalidateQueries({
          queryKey: portfolioQueryKeys.summary(portfolioId),
        }),
      ])
    },
  })
}
