import type {
  PortfolioListQuery,
  PortfolioPositionListQuery,
  PortfolioValuationListQuery,
} from '@/api/types'

export const portfolioQueryKeys = {
  all: ['portfolio'] as const,

  listsRoot: () => [...portfolioQueryKeys.all, 'list'] as const,

  portfolios: (params: PortfolioListQuery = {}) =>
    [...portfolioQueryKeys.listsRoot(), params] as const,

  detailRoot: (portfolioId: string) => [...portfolioQueryKeys.all, 'detail', portfolioId] as const,

  portfolio: (portfolioId: string) =>
    [...portfolioQueryKeys.detailRoot(portfolioId), 'portfolio'] as const,

  summary: (portfolioId: string) =>
    [...portfolioQueryKeys.detailRoot(portfolioId), 'summary'] as const,

  positionsRoot: (portfolioId: string) =>
    [...portfolioQueryKeys.detailRoot(portfolioId), 'positions'] as const,

  positions: (portfolioId: string, params: PortfolioPositionListQuery = {}) =>
    [...portfolioQueryKeys.positionsRoot(portfolioId), params] as const,

  allocationRoot: (portfolioId: string) =>
    [...portfolioQueryKeys.detailRoot(portfolioId), 'allocation'] as const,

  assetAllocation: (portfolioId: string) =>
    [...portfolioQueryKeys.allocationRoot(portfolioId), 'assets'] as const,

  sectorAllocation: (portfolioId: string) =>
    [...portfolioQueryKeys.allocationRoot(portfolioId), 'sectors'] as const,

  valuationsRoot: (portfolioId: string) =>
    [...portfolioQueryKeys.detailRoot(portfolioId), 'valuations'] as const,

  valuations: (portfolioId: string, params: PortfolioValuationListQuery = {}) =>
    [...portfolioQueryKeys.valuationsRoot(portfolioId), params] as const,
}
