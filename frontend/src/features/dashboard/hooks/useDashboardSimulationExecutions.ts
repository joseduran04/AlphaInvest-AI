import { useQuery } from '@tanstack/react-query'

import { dashboardSimulationExecutionsRequest } from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardSimulationExecutions(enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.simulationExecutions(),
    queryFn: dashboardSimulationExecutionsRequest,
    enabled,
  })
}
