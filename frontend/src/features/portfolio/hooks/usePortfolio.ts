import { useQuery } from '@tanstack/react-query'

import { portfolioRequest } from '@/features/portfolio/api/portfolioApi'
import { portfolioQueryKeys } from '@/features/portfolio/hooks/portfolioQueryKeys'

export function usePortfolio(portfolioId: string | null, enabled = true) {
  return useQuery({
    queryKey: portfolioQueryKeys.portfolio(portfolioId ?? 'none'),
    queryFn: () => {
      if (!portfolioId) {
        throw new Error('Se requiere un portafolio para consultar su detalle')
      }

      return portfolioRequest(portfolioId)
    },
    enabled: enabled && portfolioId !== null,
  })
}
