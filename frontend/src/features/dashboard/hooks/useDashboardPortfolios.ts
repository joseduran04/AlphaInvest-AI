import { useQuery } from '@tanstack/react-query'

import { dashboardPortfoliosRequest } from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardPortfolios(enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.portfolios(),
    queryFn: dashboardPortfoliosRequest,
    enabled,
  })
}
