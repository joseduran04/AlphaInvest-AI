import { useQuery } from '@tanstack/react-query'

import type { SimulationReportListQuery } from '@/api/types'
import { simulationReportsRequest } from '@/features/reporting/api/reportingApi'
import { reportingQueryKeys } from '@/features/reporting/hooks/reportingQueryKeys'

export function useSimulationReports(params: SimulationReportListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: reportingQueryKeys.simulationReports(params),
    queryFn: () => simulationReportsRequest(params),
    enabled,
  })
}
