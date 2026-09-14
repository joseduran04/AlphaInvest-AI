import { useQuery } from '@tanstack/react-query'

import { portfolioSectorAllocationRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function usePortfolioSectorAllocation(portfolioId: string | null, enabled = true) {
  return useQuery({
    queryKey: portfolioQueryKeys.sectorAllocation(portfolioId ?? 'none'),
    queryFn: () => {
      if (!portfolioId) {
        throw new Error('Se requiere un portafolio para consultar su distribución por sector')
      }

      return portfolioSectorAllocationRequest(portfolioId)
    },
    enabled: enabled && portfolioId !== null,
  })
}
