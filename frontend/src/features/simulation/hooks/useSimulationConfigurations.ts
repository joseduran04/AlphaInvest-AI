import { useQuery } from '@tanstack/react-query'

import type { SimulationConfigurationListQuery } from '@/api/types'
import { simulationConfigurationsRequest } from '@/features/simulation/api/simulationApi'
import { simulationQueryKeys } from '@/features/simulation/hooks/simulationQueryKeys'

export function useSimulationConfigurations(
  params: SimulationConfigurationListQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: simulationQueryKeys.configurations(params),
    queryFn: () => simulationConfigurationsRequest(params),
    enabled,
  })
}
