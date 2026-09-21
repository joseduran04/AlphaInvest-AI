import { useQuery } from '@tanstack/react-query'

import type { AssetReportListQuery } from '@/api/types'
import { assetReportsRequest } from '@/features/reporting/api/reportingApi'
import { reportingQueryKeys } from '@/features/reporting/hooks/reportingQueryKeys'

export function useAssetReports(params: AssetReportListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: reportingQueryKeys.assetReports(params),
    queryFn: () => assetReportsRequest(params),
    enabled,
  })
}
