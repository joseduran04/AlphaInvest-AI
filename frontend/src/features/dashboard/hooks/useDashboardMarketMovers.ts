import { keepPreviousData, useQuery } from '@tanstack/react-query'

import {
  dashboardMarketMoversRequest,
  type MarketMoversPeriod,
} from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardMarketMovers(period: MarketMoversPeriod = 'DIA', enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.marketMovers(period),
    queryFn: () => dashboardMarketMoversRequest(period),
    placeholderData: keepPreviousData,
    enabled,
  })
}
