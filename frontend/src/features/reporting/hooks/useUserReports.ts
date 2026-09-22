import { useQuery } from '@tanstack/react-query'

import type { UserReportListQuery } from '@/api/types'
import { userReportsRequest } from '@/features/reporting/api/reportingApi'
import { reportingQueryKeys } from '@/features/reporting/hooks/reportingQueryKeys'

export function useUserReports(params: UserReportListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: reportingQueryKeys.userReports(params),
    queryFn: () => userReportsRequest(params),
    enabled,
  })
}
