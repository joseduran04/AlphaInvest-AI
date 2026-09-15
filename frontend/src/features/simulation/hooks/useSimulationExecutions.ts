import { useQuery } from '@tanstack/react-query'

import type { SimulationExecutionListQuery } from '@/api/types'
import { simulationExecutionsRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

const ACTIVE_EXECUTION_STATUSES = new Set(['PENDIENTE', 'EJECUTANDO'])

export function useSimulationExecutions(params: SimulationExecutionListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: simulationQueryKeys.executions(params),
    queryFn: () => simulationExecutionsRequest(params),
    enabled,
    refetchInterval: (query) => {
      const executions = query.state.data?.items ?? []

      const hasActiveExecution = executions.some((execution) =>
        ACTIVE_EXECUTION_STATUSES.has(execution.estado),
      )

      return hasActiveExecution ? 3_000 : false
    },
  })
}
