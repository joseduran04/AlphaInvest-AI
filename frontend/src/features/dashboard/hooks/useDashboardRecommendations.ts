import { useQuery } from '@tanstack/react-query'

import { dashboardRecommendationsRequest } from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardRecommendations(enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.recommendations(),
    queryFn: dashboardRecommendationsRequest,
    enabled,
  })
}
