import { useMutation, useQueryClient } from '@tanstack/react-query'

import { cancelSimulationExecutionRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useCancelSimulationExecution(executionId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => cancelSimulationExecutionRequest(executionId),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: simulationQueryKeys.executionListsRoot(),
        }),
        queryClient.invalidateQueries({
          queryKey: simulationQueryKeys.executionDetailRoot(executionId),
        }),
      ])
    },
  })
}
