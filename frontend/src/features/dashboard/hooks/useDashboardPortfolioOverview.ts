import { useQuery } from '@tanstack/react-query'

import { dashboardPortfolioOverviewRequest } from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardPortfolioOverview(portfolioId: string | null, enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.portfolioOverview(portfolioId ?? 'none'),
    queryFn: () => {
      if (!portfolioId) {
        throw new Error('Se requiere un portafolio para consultar su resumen')
      }

      return dashboardPortfolioOverviewRequest(portfolioId)
    },
    enabled: enabled && portfolioId !== null,
  })
}
