import type {
  AssetReportListQuery,
  PortfolioReportListQuery,
  RecommendationReportListQuery,
  SimulationReportListQuery,
} from '@/api/types'

export const reportingQueryKeys = {
  all: ['reporting'] as const,

  assetReportsRoot: () => [...reportingQueryKeys.all, 'assets', 'list'] as const,

  assetReports: (params: AssetReportListQuery = {}) =>
    [...reportingQueryKeys.assetReportsRoot(), params] as const,

  portfolioReportsRoot: () => [...reportingQueryKeys.all, 'portfolios', 'list'] as const,

  portfolioReports: (params: PortfolioReportListQuery = {}) =>
    [...reportingQueryKeys.portfolioReportsRoot(), params] as const,

  simulationReportsRoot: () => [...reportingQueryKeys.all, 'simulations', 'list'] as const,

  simulationReports: (params: SimulationReportListQuery = {}) =>
    [...reportingQueryKeys.simulationReportsRoot(), params] as const,

  recommendationReportsRoot: () => [...reportingQueryKeys.all, 'recommendations', 'list'] as const,

  recommendationReports: (params: RecommendationReportListQuery = {}) =>
    [...reportingQueryKeys.recommendationReportsRoot(), params] as const,
}
