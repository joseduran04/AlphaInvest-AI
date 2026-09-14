import { useQuery } from '@tanstack/react-query'

import { simulationExecutionResultRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useSimulationResult(executionId: string | null, enabled = true) {
  return useQuery({
    queryKey: simulationQueryKeys.result(executionId ?? 'none'),
    queryFn: () => {
      if (!executionId) {
        throw new Error('Se requiere una ejecución para consultar sus resultados')
      }

      return simulationExecutionResultRequest(executionId)
    },
    enabled: enabled && executionId !== null,
  })
}
