import type {
  AssetReportListQuery,
  AuditReportListQuery,
  OperationJobReportListQuery,
  PortfolioReportListQuery,
  SimulationReportListQuery,
  UserReportListQuery,
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

  adminReportsRoot: () => [...reportingQueryKeys.all, 'admin'] as const,

  userReportsRoot: () => [...reportingQueryKeys.adminReportsRoot(), 'users', 'list'] as const,

  userReports: (params: UserReportListQuery = {}) =>
    [...reportingQueryKeys.userReportsRoot(), params] as const,

  auditReportsRoot: () => [...reportingQueryKeys.adminReportsRoot(), 'audit', 'list'] as const,

  auditReports: (params: AuditReportListQuery = {}) =>
    [...reportingQueryKeys.auditReportsRoot(), params] as const,

  operationJobReportsRoot: () =>
    [...reportingQueryKeys.adminReportsRoot(), 'jobs', 'list'] as const,

  operationJobReports: (params: OperationJobReportListQuery = {}) =>
    [...reportingQueryKeys.operationJobReportsRoot(), params] as const,
}
