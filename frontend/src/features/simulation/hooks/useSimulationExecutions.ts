import { useQuery } from '@tanstack/react-query'

import type { SimulationExecutionListQuery } from '@/api/types'
import { simulationExecutionsRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useSimulationExecutions(params: SimulationExecutionListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: simulationQueryKeys.executions(params),
    queryFn: () => simulationExecutionsRequest(params),
    enabled,
  })
}
