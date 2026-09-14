import { useQuery } from '@tanstack/react-query'

import type { PortfolioPositionListQuery } from '@/api/types'
import { portfolioPositionsRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function usePortfolioPositions(
  portfolioId: string | null,
  params: PortfolioPositionListQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: portfolioQueryKeys.positions(portfolioId ?? 'none', params),
    queryFn: () => {
      if (!portfolioId) {
        throw new Error('Se requiere un portafolio para consultar sus posiciones')
      }

      return portfolioPositionsRequest(portfolioId, params)
    },
    enabled: enabled && portfolioId !== null,
  })
}
