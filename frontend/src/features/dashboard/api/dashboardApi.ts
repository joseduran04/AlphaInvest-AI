import { apiClient } from '@/api/client'
import type {
  AssetListResponse,
  PortfolioListResponse,
  PortfolioOverviewResponse,
  SimulationExecutionListResponse,
} from '@/api/types'

const PORTFOLIOS_PATH = '/api/v1/portfolios'
const SIMULATION_EXECUTIONS_PATH = '/api/v1/simulations/executions'
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

export async function dashboardAssetsRequest(): Promise<AssetListResponse> {
  const response = await apiClient.get<AssetListResponse>(ASSETS_PATH, {
    params: {
      limit: 5,
      offset: 0,
    },
  })

  return response.data
}
