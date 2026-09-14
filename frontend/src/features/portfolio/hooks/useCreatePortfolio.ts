import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { PortfolioCreateRequest } from '@/api/types'
import { createPortfolioRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function useCreatePortfolio() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: PortfolioCreateRequest) => createPortfolioRequest(data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: portfolioQueryKeys.listsRoot(),
      })
    },
  })
}
