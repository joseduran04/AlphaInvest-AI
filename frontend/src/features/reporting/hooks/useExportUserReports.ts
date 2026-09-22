import { useMutation } from '@tanstack/react-query'

import type { UserReportExportQuery } from '@/api/types'
import { exportUserReportsRequest, saveReportDownload } from '@/features/reporting/api/reportingApi'

export function useExportUserReports() {
  return useMutation({
    mutationFn: (params: UserReportExportQuery = {}) => exportUserReportsRequest(params),
    onSuccess: saveReportDownload,
  })
}
