import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { SimulationConfigurationAssetCreateRequest } from '@/api/types'
import { addSimulationConfigurationAssetRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useAddSimulationAsset(configurationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: SimulationConfigurationAssetCreateRequest) =>
      addSimulationConfigurationAssetRequest(configurationId, data),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: simulationQueryKeys.configurationAssetsRoot(configurationId),
        }),
        queryClient.invalidateQueries({
          queryKey: simulationQueryKeys.distribution(configurationId),
        }),
      ])
    },
  })
}
