import { useQuery } from '@tanstack/react-query'

import { simulationConfigurationRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useSimulationConfiguration(configurationId: string | null, enabled = true) {
  return useQuery({
    queryKey: simulationQueryKeys.configuration(configurationId ?? 'none'),
    queryFn: () => {
      if (!configurationId) {
        throw new Error('Se requiere una configuración para consultar su detalle')
      }

      return simulationConfigurationRequest(configurationId)
    },
    enabled: enabled && configurationId !== null,
  })
}
