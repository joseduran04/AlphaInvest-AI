import { useMutation } from '@tanstack/react-query'

import type { SimulationReportExportQuery } from '@/api/types'
import {
  exportSimulationReportsRequest,
  saveReportDownload,
} from '@/features/reporting/api/reportingApi'

export function useExportSimulationReports() {
  return useMutation({
    mutationFn: (params: SimulationReportExportQuery = {}) =>
      exportSimulationReportsRequest(params),
    onSuccess: saveReportDownload,
  })
}
