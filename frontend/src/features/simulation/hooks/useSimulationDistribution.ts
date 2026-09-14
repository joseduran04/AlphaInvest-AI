import { useQuery } from '@tanstack/react-query'

import { simulationDistributionRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useSimulationDistribution(configurationId: string | null, enabled = true) {
  return useQuery({
    queryKey: simulationQueryKeys.distribution(configurationId ?? 'none'),
    queryFn: () => {
      if (!configurationId) {
        throw new Error('Se requiere una configuración para consultar su distribución')
      }

      return simulationDistributionRequest(configurationId)
    },
    enabled: enabled && configurationId !== null,
  })
}
