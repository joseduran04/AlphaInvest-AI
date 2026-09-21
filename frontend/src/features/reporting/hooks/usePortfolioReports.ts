import { useQuery } from '@tanstack/react-query'

import type { PortfolioReportListQuery } from '@/api/types'
import { portfolioReportsRequest } from '@/features/reporting/api/reportingApi'
import { reportingQueryKeys } from '@/features/reporting/hooks/reportingQueryKeys'

export function usePortfolioReports(params: PortfolioReportListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: reportingQueryKeys.portfolioReports(params),
    queryFn: () => portfolioReportsRequest(params),
    enabled,
  })
}
