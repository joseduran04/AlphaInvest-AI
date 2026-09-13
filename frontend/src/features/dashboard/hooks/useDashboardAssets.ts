import { useQuery } from '@tanstack/react-query'

import { dashboardAssetsRequest } from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardAssets(enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.assets(),
    queryFn: dashboardAssetsRequest,
    enabled,
  })
}
