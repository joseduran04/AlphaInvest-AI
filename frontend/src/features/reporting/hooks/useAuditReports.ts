import { useQuery } from '@tanstack/react-query'

import type { AuditReportListQuery } from '@/api/types'
import { auditReportsRequest } from '@/features/reporting/api/reportingApi'
import { reportingQueryKeys } from '@/features/reporting/hooks/reportingQueryKeys'

export function useAuditReports(params: AuditReportListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: reportingQueryKeys.auditReports(params),
    queryFn: () => auditReportsRequest(params),
    enabled,
  })
}
