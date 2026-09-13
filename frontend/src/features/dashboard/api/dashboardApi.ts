import { apiClient } from '@/api/client'
import type {
  AssetListResponse,
  NotificationListResponse,
  PortfolioListResponse,
  PortfolioOverviewResponse,
  RecommendationReportListResponse,
  SimulationExecutionListResponse,
  UnreadNotificationCountResponse,
} from '@/api/types'

const PORTFOLIOS_PATH = '/api/v1/portfolios'
const SIMULATION_EXECUTIONS_PATH = '/api/v1/simulations/executions'
const NOTIFICATIONS_PATH = '/api/v1/notifications'
const UNREAD_NOTIFICATION_COUNT_PATH = '/api/v1/notifications/unread-count'
const RECOMMENDATIONS_REPORT_PATH = '/api/v1/reports/recommendations'
const ASSETS_PATH = '/api/v1/market/assets'

export async function dashboardPortfoliosRequest(): Promise<PortfolioListResponse> {
  const response = await apiClient.get<PortfolioListResponse>(PORTFOLIOS_PATH, {
    params: {
      estado: 'ACTIVO',
      limit: 5,
      offset: 0,
    },
  })

  return response.data
}

export async function dashboardPortfolioOverviewRequest(
  portfolioId: string,
): Promise<PortfolioOverviewResponse> {
  const response = await apiClient.get<PortfolioOverviewResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/summary`,
  )

  return response.data
}

export async function dashboardSimulationExecutionsRequest(): Promise<SimulationExecutionListResponse> {
  const response = await apiClient.get<SimulationExecutionListResponse>(
    SIMULATION_EXECUTIONS_PATH,
    {
      params: {
        limit: 5,
        offset: 0,
      },
    },
  )

  return response.data
}

export async function dashboardUnreadNotificationCountRequest(): Promise<UnreadNotificationCountResponse> {
  const response = await apiClient.get<UnreadNotificationCountResponse>(
    UNREAD_NOTIFICATION_COUNT_PATH,
  )

  return response.data
}

export async function dashboardNotificationsRequest(): Promise<NotificationListResponse> {
  const response = await apiClient.get<NotificationListResponse>(NOTIFICATIONS_PATH, {
    params: {
      limit: 5,
      offset: 0,
    },
  })

  return response.data
}

export async function dashboardRecommendationsRequest(): Promise<RecommendationReportListResponse> {
  const response = await apiClient.get<RecommendationReportListResponse>(
    RECOMMENDATIONS_REPORT_PATH,
    {
      params: {
        limit: 5,
        offset: 0,
      },
    },
  )

  return response.data
}

export async function dashboardAssetsRequest(): Promise<AssetListResponse> {
  const response = await apiClient.get<AssetListResponse>(ASSETS_PATH, {
    params: {
      limit: 5,
      offset: 0,
    },
  })

  return response.data
}
