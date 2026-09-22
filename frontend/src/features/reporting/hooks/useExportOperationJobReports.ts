import { useMutation } from '@tanstack/react-query'

import type { OperationJobReportExportQuery } from '@/api/types'
import {
  exportOperationJobReportsRequest,
  saveReportDownload,
} from '@/features/reporting/api/reportingApi'

export function useExportOperationJobReports() {
  return useMutation({
    mutationFn: (params: OperationJobReportExportQuery = {}) =>
      exportOperationJobReportsRequest(params),
    onSuccess: saveReportDownload,
  })
}
