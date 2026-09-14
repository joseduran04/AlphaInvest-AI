import { useQuery } from '@tanstack/react-query'

import type { PortfolioValuationListQuery } from '@/api/types'
import { portfolioValuationsRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function usePortfolioValuations(
  portfolioId: string | null,
  params: PortfolioValuationListQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: portfolioQueryKeys.valuations(portfolioId ?? 'none', params),
    queryFn: () => {
      if (!portfolioId) {
        throw new Error('Se requiere un portafolio para consultar sus valoraciones')
      }

      return portfolioValuationsRequest(portfolioId, params)
    },
    enabled: enabled && portfolioId !== null,
  })
}
