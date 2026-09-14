import { useMutation, useQueryClient } from '@tanstack/react-query'

import { markSimulationConfigurationReadyRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useMarkSimulationReady(configurationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => markSimulationConfigurationReadyRequest(configurationId),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: simulationQueryKeys.configurationListsRoot(),
        }),
        queryClient.invalidateQueries({
          queryKey: simulationQueryKeys.configurationDetailRoot(configurationId),
        }),
      ])
    },
  })
}
