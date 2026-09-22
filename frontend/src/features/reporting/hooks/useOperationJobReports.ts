import { useQuery } from '@tanstack/react-query'

import type { OperationJobReportListQuery } from '@/api/types'
import { operationJobReportsRequest } from '@/features/reporting/api/reportingApi'
import { reportingQueryKeys } from '@/features/reporting/hooks/reportingQueryKeys'

export function useOperationJobReports(params: OperationJobReportListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: reportingQueryKeys.operationJobReports(params),
    queryFn: () => operationJobReportsRequest(params),
    enabled,
  })
}
