import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { SimulationExecutionCreateRequest } from '@/api/types'
import { createSimulationExecutionRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useCreateSimulationExecution() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: SimulationExecutionCreateRequest) => createSimulationExecutionRequest(data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: simulationQueryKeys.executionListsRoot(),
      })
    },
  })
}
