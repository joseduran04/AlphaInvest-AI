export const dashboardQueryKeys = {
  all: ['dashboard'] as const,

  portfolios: () => [...dashboardQueryKeys.all, 'portfolios'] as const,
  portfolioOverview: (portfolioId: string) =>
    [...dashboardQueryKeys.portfolios(), 'overview', portfolioId] as const,

  simulationExecutions: () => [...dashboardQueryKeys.all, 'simulation-executions'] as const,

  unreadNotificationCount: () =>
    [...dashboardQueryKeys.all, 'notifications', 'unread-count'] as const,
  notifications: () => [...dashboardQueryKeys.all, 'notifications', 'list'] as const,

  recommendations: () => [...dashboardQueryKeys.all, 'recommendations'] as const,

  assets: () => [...dashboardQueryKeys.all, 'assets'] as const,
}
