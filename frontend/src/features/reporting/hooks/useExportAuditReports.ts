import { useMutation } from '@tanstack/react-query'

import type { AuditReportExportQuery } from '@/api/types'
import {
  exportAuditReportsRequest,
  saveReportDownload,
} from '@/features/reporting/api/reportingApi'

export function useExportAuditReports() {
  return useMutation({
    mutationFn: (params: AuditReportExportQuery = {}) => exportAuditReportsRequest(params),
    onSuccess: saveReportDownload,
  })
}
