import { useMutation, useQueryClient } from '@tanstack/react-query'

import { archiveSimulationConfigurationRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useArchiveSimulationConfiguration(configurationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => archiveSimulationConfigurationRequest(configurationId),

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
