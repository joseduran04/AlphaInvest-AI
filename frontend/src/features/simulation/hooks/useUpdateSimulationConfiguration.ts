import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { SimulationConfigurationUpdateRequest } from '@/api/types'
import { updateSimulationConfigurationRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useUpdateSimulationConfiguration(configurationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: SimulationConfigurationUpdateRequest) =>
      updateSimulationConfigurationRequest(configurationId, data),

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
