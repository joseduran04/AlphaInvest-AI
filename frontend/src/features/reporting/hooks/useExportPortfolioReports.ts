import { useMutation } from '@tanstack/react-query'

import type { PortfolioReportExportQuery } from '@/api/types'
import {
  exportPortfolioReportsRequest,
  saveReportDownload,
} from '@/features/reporting/api/reportingApi'

export function useExportPortfolioReports() {
  return useMutation({
    mutationFn: (params: PortfolioReportExportQuery = {}) => exportPortfolioReportsRequest(params),
    onSuccess: saveReportDownload,
  })
}
