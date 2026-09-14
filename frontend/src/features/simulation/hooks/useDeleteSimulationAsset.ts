import { useMutation, useQueryClient } from '@tanstack/react-query'

import { deleteSimulationConfigurationAssetRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useDeleteSimulationAsset(configurationId: string, assetId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => deleteSimulationConfigurationAssetRequest(configurationId, assetId),

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
