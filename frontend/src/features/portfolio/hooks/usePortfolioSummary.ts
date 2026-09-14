import { useQuery } from '@tanstack/react-query'

import { portfolioSummaryRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function usePortfolioSummary(portfolioId: string | null, enabled = true) {
  return useQuery({
    queryKey: portfolioQueryKeys.summary(portfolioId ?? 'none'),
    queryFn: () => {
      if (!portfolioId) {
        throw new Error('Se requiere un portafolio para consultar su resumen')
      }

      return portfolioSummaryRequest(portfolioId)
    },
    enabled: enabled && portfolioId !== null,
  })
}
