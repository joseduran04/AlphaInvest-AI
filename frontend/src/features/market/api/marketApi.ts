import { apiClient } from '@/api/client'
import type {
  PriceSeriesResponse,
  AssetListQuery,
  AssetListResponse,
  AssetResponse,
  AssetTypeListQuery,
  AssetTypeListResponse,
  FinancialIndicatorListQuery,
  FinancialIndicatorListResponse,
  FinancialSourceListQuery,
  FinancialSourceListResponse,
  HistoricalPriceListQuery,
  HistoricalPriceListResponse,
  IndicatorCalculationRequest,
  IndicatorCalculationResponse,
  JobExecutionListResponse,
  JobExecutionResponse,
  LatestPriceQuery,
  LatestPriceResponse,
  MarketListQuery,
  MarketListResponse,
  MarketSynchronizationListQuery,
  PriceSynchronizationResponse,
} from '@/api/types'

const MARKETS_PATH = '/api/v1/market/markets'
const ASSET_TYPES_PATH = '/api/v1/market/asset-types'
const FINANCIAL_SOURCES_PATH = '/api/v1/market/sources'
const ASSETS_PATH = '/api/v1/market/assets'
const MARKET_SYNCHRONIZATIONS_PATH = '/api/v1/market/synchronizations'

export async function marketsRequest(params: MarketListQuery = {}): Promise<MarketListResponse> {
  const response = await apiClient.get<MarketListResponse>(MARKETS_PATH, {
    params,
  })

  return response.data
}

export async function assetTypesRequest(
  params: AssetTypeListQuery = {},
): Promise<AssetTypeListResponse> {
  const response = await apiClient.get<AssetTypeListResponse>(ASSET_TYPES_PATH, {
    params,
  })

  return response.data
}

export async function financialSourcesRequest(
  params: FinancialSourceListQuery = {},
): Promise<FinancialSourceListResponse> {
  const response = await apiClient.get<FinancialSourceListResponse>(FINANCIAL_SOURCES_PATH, {
    params,
  })

  return response.data
}

export async function assetsRequest(params: AssetListQuery = {}): Promise<AssetListResponse> {
  const response = await apiClient.get<AssetListResponse>(ASSETS_PATH, {
    params,
  })

  return response.data
}

export async function assetRequest(assetId: string): Promise<AssetResponse> {
  const response = await apiClient.get<AssetResponse>(`${ASSETS_PATH}/${assetId}`)

  return response.data
}

export async function historicalPricesRequest(
  assetId: string,
  params: HistoricalPriceListQuery = {},
): Promise<HistoricalPriceListResponse> {
  const response = await apiClient.get<HistoricalPriceListResponse>(
    `${ASSETS_PATH}/${assetId}/prices`,
    {
      params,
    },
  )

  return response.data
}

export async function latestPriceRequest(
  assetId: string,
  params: LatestPriceQuery = {},
): Promise<LatestPriceResponse> {
  const response = await apiClient.get<LatestPriceResponse>(
    `${ASSETS_PATH}/${assetId}/latest-price`,
    {
      params,
    },
  )

  return response.data
}

export async function synchronizeAssetPricesRequest(
  assetId: string,
): Promise<PriceSynchronizationResponse> {
  const response = await apiClient.post<PriceSynchronizationResponse>(
    `${ASSETS_PATH}/${assetId}/prices/sync`,
    undefined,
    // Descargar el histórico completo puede tardar más que el límite general.
    { timeout: 60_000 },
  )

  return response.data
}

export async function assetIndicatorsRequest(
  assetId: string,
  params: FinancialIndicatorListQuery = {},
): Promise<FinancialIndicatorListResponse> {
  const response = await apiClient.get<FinancialIndicatorListResponse>(
    `${ASSETS_PATH}/${assetId}/indicators`,
    {
      params,
    },
  )

  return response.data
}

export async function calculateAssetIndicatorsRequest(
  assetId: string,
  data: IndicatorCalculationRequest,
): Promise<IndicatorCalculationResponse> {
  const response = await apiClient.post<IndicatorCalculationResponse>(
    `${ASSETS_PATH}/${assetId}/indicators/calculate`,
    data,
  )

  return response.data
}

export async function marketSynchronizationsRequest(
  params: MarketSynchronizationListQuery = {},
): Promise<JobExecutionListResponse> {
  const response = await apiClient.get<JobExecutionListResponse>(MARKET_SYNCHRONIZATIONS_PATH, {
    params,
  })

  return response.data
}

export async function marketSynchronizationRequest(
  executionId: string,
): Promise<JobExecutionResponse> {
  const response = await apiClient.get<JobExecutionResponse>(
    `${MARKET_SYNCHRONIZATIONS_PATH}/${executionId}`,
  )

  return response.data
}

export async function priceSeriesRequest(
  assetId: string,
  startDate: string | null,
): Promise<PriceSeriesResponse> {
  const response = await apiClient.get<PriceSeriesResponse>(
    `${ASSETS_PATH}/${assetId}/price-series`,
    {
      params: {
        start_date: startDate ?? undefined,
        max_points: 800,
      },
    },
  )

  return response.data
}
