import { apiClient } from '@/api/client'
import type {
  AssetAllocationResponse,
  PortfolioCloseResponse,
  PortfolioCreateRequest,
  PortfolioListQuery,
  PortfolioListResponse,
  PortfolioOverviewResponse,
  PortfolioPositionListQuery,
  PortfolioResponse,
  PortfolioUpdateRequest,
  PortfolioValuationCreateRequest,
  PortfolioValuationListQuery,
  PortfolioValuationListResponse,
  PortfolioValuationResponse,
  PositionCreateRequest,
  PositionListResponse,
  PositionResponse,
  PositionUpdateRequest,
  SectorAllocationResponse,
} from '@/api/types'

const PORTFOLIOS_PATH = '/api/v1/portfolios'

export async function portfoliosRequest(
  params: PortfolioListQuery = {},
): Promise<PortfolioListResponse> {
  const response = await apiClient.get<PortfolioListResponse>(PORTFOLIOS_PATH, {
    params,
  })

  return response.data
}

export async function portfolioRequest(portfolioId: string): Promise<PortfolioResponse> {
  const response = await apiClient.get<PortfolioResponse>(`${PORTFOLIOS_PATH}/${portfolioId}`)

  return response.data
}

export async function createPortfolioRequest(
  data: PortfolioCreateRequest,
): Promise<PortfolioResponse> {
  const response = await apiClient.post<PortfolioResponse>(PORTFOLIOS_PATH, data)

  return response.data
}

export async function updatePortfolioRequest(
  portfolioId: string,
  data: PortfolioUpdateRequest,
): Promise<PortfolioResponse> {
  const response = await apiClient.patch<PortfolioResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}`,
    data,
  )

  return response.data
}

export async function portfolioSummaryRequest(
  portfolioId: string,
): Promise<PortfolioOverviewResponse> {
  const response = await apiClient.get<PortfolioOverviewResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/summary`,
  )

  return response.data
}

export async function portfolioAssetAllocationRequest(
  portfolioId: string,
): Promise<AssetAllocationResponse> {
  const response = await apiClient.get<AssetAllocationResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/allocation/assets`,
  )

  return response.data
}

export async function portfolioSectorAllocationRequest(
  portfolioId: string,
): Promise<SectorAllocationResponse> {
  const response = await apiClient.get<SectorAllocationResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/allocation/sectors`,
  )

  return response.data
}

export async function portfolioValuationsRequest(
  portfolioId: string,
  params: PortfolioValuationListQuery = {},
): Promise<PortfolioValuationListResponse> {
  const response = await apiClient.get<PortfolioValuationListResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/valuations`,
    {
      params,
    },
  )

  return response.data
}

export async function createPortfolioValuationRequest(
  portfolioId: string,
  data: PortfolioValuationCreateRequest,
): Promise<PortfolioValuationResponse> {
  const response = await apiClient.post<PortfolioValuationResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/valuations`,
    data,
  )

  return response.data
}

export async function closePortfolioRequest(portfolioId: string): Promise<PortfolioCloseResponse> {
  const response = await apiClient.post<PortfolioCloseResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/close`,
  )

  return response.data
}

export async function portfolioPositionsRequest(
  portfolioId: string,
  params: PortfolioPositionListQuery = {},
): Promise<PositionListResponse> {
  const response = await apiClient.get<PositionListResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/positions`,
    {
      params,
    },
  )

  return response.data
}

export async function createPositionRequest(
  portfolioId: string,
  data: PositionCreateRequest,
): Promise<PositionResponse> {
  const response = await apiClient.post<PositionResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/positions`,
    data,
  )

  return response.data
}

export async function updatePositionRequest(
  portfolioId: string,
  positionId: string,
  data: PositionUpdateRequest,
): Promise<PositionResponse> {
  const response = await apiClient.patch<PositionResponse>(
    `${PORTFOLIOS_PATH}/${portfolioId}/positions/${positionId}`,
    data,
  )

  return response.data
}

export async function deletePositionRequest(
  portfolioId: string,
  positionId: string,
): Promise<void> {
  await apiClient.delete(`${PORTFOLIOS_PATH}/${portfolioId}/positions/${positionId}`)
}
