import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { SimulationConfigurationCreateRequest } from '@/api/types'
import { createSimulationConfigurationRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useCreateSimulationConfiguration() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: SimulationConfigurationCreateRequest) =>
      createSimulationConfigurationRequest(data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: simulationQueryKeys.configurationListsRoot(),
      })
    },
  })
}
