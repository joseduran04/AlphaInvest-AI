import { useQuery } from '@tanstack/react-query'

import type { RecommendationReportListQuery } from '@/api/types'
import { recommendationReportsRequest } from '@/features/reporting/api/reportingApi'
import { reportingQueryKeys } from '@/features/reporting/hooks/reportingQueryKeys'

export function useRecommendationReports(
  params: RecommendationReportListQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: reportingQueryKeys.recommendationReports(params),
    queryFn: () => recommendationReportsRequest(params),
    enabled,
  })
}
