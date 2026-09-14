import { useMutation, useQueryClient } from '@tanstack/react-query'

import type { SimulationConfigurationAssetUpdateRequest } from '@/api/types'
import { updateSimulationConfigurationAssetRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useUpdateSimulationAsset(configurationId: string, assetId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: SimulationConfigurationAssetUpdateRequest) =>
      updateSimulationConfigurationAssetRequest(configurationId, assetId, data),

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
