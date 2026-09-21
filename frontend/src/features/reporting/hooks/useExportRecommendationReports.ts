import { useMutation } from '@tanstack/react-query'

import type { RecommendationReportExportQuery } from '@/api/types'
import {
  exportRecommendationReportsRequest,
  saveReportDownload,
} from '@/features/reporting/api/reportingApi'

export function useExportRecommendationReports() {
  return useMutation({
    mutationFn: (params: RecommendationReportExportQuery = {}) =>
      exportRecommendationReportsRequest(params),
    onSuccess: saveReportDownload,
  })
}
