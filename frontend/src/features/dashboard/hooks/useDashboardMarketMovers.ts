import { useQuery } from '@tanstack/react-query'

import { dashboardMarketMoversRequest } from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardMarketMovers(enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.marketMovers(),
    queryFn: dashboardMarketMoversRequest,
    enabled,
  })
}
