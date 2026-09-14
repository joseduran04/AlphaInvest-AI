import { useQuery } from '@tanstack/react-query'

import { portfolioAssetAllocationRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function usePortfolioAssetAllocation(portfolioId: string | null, enabled = true) {
  return useQuery({
    queryKey: portfolioQueryKeys.assetAllocation(portfolioId ?? 'none'),
    queryFn: () => {
      if (!portfolioId) {
        throw new Error('Se requiere un portafolio para consultar su distribución por activo')
      }

      return portfolioAssetAllocationRequest(portfolioId)
    },
    enabled: enabled && portfolioId !== null,
  })
}
