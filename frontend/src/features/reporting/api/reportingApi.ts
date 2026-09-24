import { apiClient } from '@/api/client'
import type {
  AssetReportExportQuery,
  AssetReportListQuery,
  AssetReportListResponse,
  AuditDailyReportListResponse,
  AuditReportExportQuery,
  AuditReportListQuery,
  OperationJobReportExportQuery,
  OperationJobReportListQuery,
  OperationJobReportListResponse,
  PortfolioReportExportQuery,
  PortfolioReportListQuery,
  PortfolioReportListResponse,
  SimulationReportExportQuery,
  SimulationReportListQuery,
  SimulationReportListResponse,
  UserReportExportQuery,
  UserReportListQuery,
  UserReportListResponse,
} from '@/api/types'

const REPORTS_PATH = '/api/v1/reports'

interface ReportDownload {
  blob: Blob
  filename: string
}

function getDownloadFilename(contentDisposition: string | undefined, fallback: string): string {
  if (!contentDisposition) {
    return fallback
  }

  const encodedFilenameMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i)

  if (encodedFilenameMatch?.[1]) {
    try {
      return decodeURIComponent(encodedFilenameMatch[1])
    } catch {
      return encodedFilenameMatch[1]
    }
  }

  const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i)

  return filenameMatch?.[1] ?? fallback
}

async function downloadReportRequest(
  path: string,
  params: Record<string, unknown>,
  fallbackFilename: string,
): Promise<ReportDownload> {
  const response = await apiClient.get<Blob>(path, {
    params,
    responseType: 'blob',
  })

  return {
    blob: response.data,
    filename: getDownloadFilename(response.headers['content-disposition'], fallbackFilename),
  }
}

export async function assetReportsRequest(
  params: AssetReportListQuery = {},
): Promise<AssetReportListResponse> {
  const response = await apiClient.get<AssetReportListResponse>(`${REPORTS_PATH}/assets`, {
    params,
  })

  return response.data
}

export async function portfolioReportsRequest(
  params: PortfolioReportListQuery = {},
): Promise<PortfolioReportListResponse> {
  const response = await apiClient.get<PortfolioReportListResponse>(`${REPORTS_PATH}/portfolios`, {
    params,
  })

  return response.data
}

export async function simulationReportsRequest(
  params: SimulationReportListQuery = {},
): Promise<SimulationReportListResponse> {
  const response = await apiClient.get<SimulationReportListResponse>(
    `${REPORTS_PATH}/simulations`,
    {
      params,
    },
  )

  return response.data
}

export async function userReportsRequest(
  params: UserReportListQuery = {},
): Promise<UserReportListResponse> {
  const response = await apiClient.get<UserReportListResponse>(`${REPORTS_PATH}/admin/users`, {
    params,
  })

  return response.data
}

export async function auditReportsRequest(
  params: AuditReportListQuery = {},
): Promise<AuditDailyReportListResponse> {
  const response = await apiClient.get<AuditDailyReportListResponse>(
    `${REPORTS_PATH}/admin/audit`,
    {
      params,
    },
  )

  return response.data
}

export async function operationJobReportsRequest(
  params: OperationJobReportListQuery = {},
): Promise<OperationJobReportListResponse> {
  const response = await apiClient.get<OperationJobReportListResponse>(
    `${REPORTS_PATH}/admin/jobs`,
    {
      params,
    },
  )

  return response.data
}

export function exportAssetReportsRequest(
  params: AssetReportExportQuery = {},
): Promise<ReportDownload> {
  return downloadReportRequest(`${REPORTS_PATH}/export/assets`, params, 'assets_report.csv')
}

export function exportPortfolioReportsRequest(
  params: PortfolioReportExportQuery = {},
): Promise<ReportDownload> {
  return downloadReportRequest(`${REPORTS_PATH}/export/portfolios`, params, 'portfolios_report.csv')
}

export function exportSimulationReportsRequest(
  params: SimulationReportExportQuery = {},
): Promise<ReportDownload> {
  return downloadReportRequest(
    `${REPORTS_PATH}/export/simulations`,
    params,
    'simulations_report.csv',
  )
}

export function exportUserReportsRequest(
  params: UserReportExportQuery = {},
): Promise<ReportDownload> {
  return downloadReportRequest(`${REPORTS_PATH}/admin/export/users`, params, 'users_report.csv')
}

export function exportAuditReportsRequest(
  params: AuditReportExportQuery = {},
): Promise<ReportDownload> {
  return downloadReportRequest(`${REPORTS_PATH}/admin/export/audit`, params, 'audit_report.csv')
}

export function exportOperationJobReportsRequest(
  params: OperationJobReportExportQuery = {},
): Promise<ReportDownload> {
  return downloadReportRequest(`${REPORTS_PATH}/admin/export/jobs`, params, 'jobs_report.csv')
}

export function saveReportDownload(download: ReportDownload): void {
  const objectUrl = URL.createObjectURL(download.blob)
  const anchor = document.createElement('a')

  anchor.href = objectUrl
  anchor.download = download.filename
  anchor.style.display = 'none'

  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()

  URL.revokeObjectURL(objectUrl)
}
