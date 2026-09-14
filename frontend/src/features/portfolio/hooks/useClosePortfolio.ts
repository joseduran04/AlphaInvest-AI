import { useMutation, useQueryClient } from '@tanstack/react-query'

import { closePortfolioRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function useClosePortfolio(portfolioId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => closePortfolioRequest(portfolioId),

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
