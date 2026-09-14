import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { PortfolioUpdateRequest } from '@/api/types'
import { updatePortfolioRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function useUpdatePortfolio(portfolioId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: PortfolioUpdateRequest) => updatePortfolioRequest(portfolioId, data),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: portfolioQueryKeys.listsRoot(),
        }),
        queryClient.invalidateQueries({
          queryKey: portfolioQueryKeys.detailRoot(portfolioId),
        }),
      ])
    },
  })
}
