import { useQuery } from '@tanstack/react-query'

import { simulationExecutionRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useSimulationExecution(executionId: string | null, enabled = true) {
  return useQuery({
    queryKey: simulationQueryKeys.execution(executionId ?? 'none'),
    queryFn: () => {
      if (!executionId) {
        throw new Error('Se requiere una ejecución para consultar su detalle')
      }

      return simulationExecutionRequest(executionId)
    },
    enabled: enabled && executionId !== null,
  })
}
