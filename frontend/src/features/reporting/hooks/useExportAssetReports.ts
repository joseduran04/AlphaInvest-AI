import { useMutation } from '@tanstack/react-query'

import type { AssetReportExportQuery } from '@/api/types'
import {
  exportAssetReportsRequest,
  saveReportDownload,
} from '@/features/reporting/api/reportingApi'

export function useExportAssetReports() {
  return useMutation({
    mutationFn: (params: AssetReportExportQuery = {}) => exportAssetReportsRequest(params),
    onSuccess: saveReportDownload,
  })
}
