import type {
  AssetListQuery,
  AssetTypeListQuery,
  FinancialIndicatorListQuery,
  FinancialSourceListQuery,
  HistoricalPriceListQuery,
  LatestPriceQuery,
  MarketListQuery,
  MarketSynchronizationListQuery,
} from '@/api/types'

export const marketQueryKeys = {
  all: ['market'] as const,

  markets: (params: MarketListQuery = {}) => [...marketQueryKeys.all, 'markets', params] as const,

  assetTypes: (params: AssetTypeListQuery = {}) =>
    [...marketQueryKeys.all, 'asset-types', params] as const,

  financialSources: (params: FinancialSourceListQuery = {}) =>
    [...marketQueryKeys.all, 'financial-sources', params] as const,

  assets: (params: AssetListQuery = {}) =>
    [...marketQueryKeys.all, 'assets', 'list', params] as const,

  asset: (assetId: string) => [...marketQueryKeys.all, 'assets', 'detail', assetId] as const,

  prices: (assetId: string) => [...marketQueryKeys.asset(assetId), 'prices'] as const,

  historicalPrices: (assetId: string, params: HistoricalPriceListQuery = {}) =>
    [...marketQueryKeys.prices(assetId), 'history', params] as const,

  latestPrice: (assetId: string, params: LatestPriceQuery = {}) =>
    [...marketQueryKeys.prices(assetId), 'latest', params] as const,

  indicatorsRoot: (assetId: string) => [...marketQueryKeys.asset(assetId), 'indicators'] as const,

  indicators: (assetId: string, params: FinancialIndicatorListQuery = {}) =>
    [...marketQueryKeys.indicatorsRoot(assetId), params] as const,

  synchronizationsRoot: () => [...marketQueryKeys.all, 'synchronizations'] as const,

  synchronizations: (params: MarketSynchronizationListQuery = {}) =>
    [...marketQueryKeys.synchronizationsRoot(), 'list', params] as const,

  synchronization: (executionId: string) =>
    [...marketQueryKeys.synchronizationsRoot(), 'detail', executionId] as const,
}
