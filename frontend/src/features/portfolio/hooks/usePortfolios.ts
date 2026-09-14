import { useQuery } from '@tanstack/react-query'

import type { PortfolioListQuery } from '@/api/types'
import { portfoliosRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function usePortfolios(params: PortfolioListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: portfolioQueryKeys.portfolios(params),
    queryFn: () => portfoliosRequest(params),
    enabled,
  })
}
