import { useQuery } from '@tanstack/react-query'

import { simulationConfigurationAssetsRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useSimulationConfigurationAssets(configurationId: string | null, enabled = true) {
  return useQuery({
    queryKey: simulationQueryKeys.configurationAssets(configurationId ?? 'none'),
    queryFn: () => {
      if (!configurationId) {
        throw new Error('Se requiere una configuración para consultar sus activos')
      }

      return simulationConfigurationAssetsRequest(configurationId)
    },
    enabled: enabled && configurationId !== null,
  })
}
