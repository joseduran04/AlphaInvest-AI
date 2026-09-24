import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router'

import { PageLoadingState } from '@/components/PageLoadingState'
import { AnyPermissionRoute } from '@/features/auth/guards/AnyPermissionRoute'
import { PermissionRoute } from '@/features/auth/guards/PermissionRoute'
import { ProtectedRoute } from '@/features/auth/guards/ProtectedRoute'
import { ApplicationLayout } from '@/layouts/ApplicationLayout'

const AdminAuditPage = lazy(() =>
  import('@/features/admin/pages/AdminAuditPage').then((module) => ({
    default: module.AdminAuditPage,
  })),
)

const AdminJobsPage = lazy(() =>
  import('@/features/admin/pages/AdminJobsPage').then((module) => ({
    default: module.AdminJobsPage,
  })),
)

const AdminNotificationsPage = lazy(() =>
  import('@/features/admin/pages/AdminNotificationsPage').then((module) => ({
    default: module.AdminNotificationsPage,
  })),
)

const AdminPage = lazy(() =>
  import('@/features/admin/pages/AdminPage').then((module) => ({
    default: module.AdminPage,
  })),
)

const AdminUsersPage = lazy(() =>
  import('@/features/admin/pages/AdminUsersPage').then((module) => ({
    default: module.AdminUsersPage,
  })),
)

const AiAnalysisPage = lazy(() =>
  import('@/features/ai/pages/AiAnalysisPage').then((module) => ({
    default: module.AiAnalysisPage,
  })),
)

const DashboardPage = lazy(() =>
  import('@/features/dashboard/pages/DashboardPage').then((module) => ({
    default: module.DashboardPage,
  })),
)

const AssetDetailPage = lazy(() =>
  import('@/features/market/pages/AssetDetailPage').then((module) => ({
    default: module.AssetDetailPage,
  })),
)

const MarketPage = lazy(() =>
  import('@/features/market/pages/MarketPage').then((module) => ({
    default: module.MarketPage,
  })),
)

const MarketSynchronizationDetailPage = lazy(() =>
  import('@/features/market/pages/MarketSynchronizationDetailPage').then((module) => ({
    default: module.MarketSynchronizationDetailPage,
  })),
)

const MarketSynchronizationsPage = lazy(() =>
  import('@/features/market/pages/MarketSynchronizationsPage').then((module) => ({
    default: module.MarketSynchronizationsPage,
  })),
)

const NewsPage = lazy(() =>
  import('@/features/news/pages/NewsPage').then((module) => ({
    default: module.NewsPage,
  })),
)

const NotificationDetailPage = lazy(() =>
  import('@/features/notifications/pages/NotificationDetailPage').then((module) => ({
    default: module.NotificationDetailPage,
  })),
)

const NotificationsPage = lazy(() =>
  import('@/features/notifications/pages/NotificationsPage').then((module) => ({
    default: module.NotificationsPage,
  })),
)

const PortfolioDetailPage = lazy(() =>
  import('@/features/portfolio/pages/PortfolioDetailPage').then((module) => ({
    default: module.PortfolioDetailPage,
  })),
)

const PortfoliosPage = lazy(() =>
  import('@/features/portfolio/pages/PortfoliosPage').then((module) => ({
    default: module.PortfoliosPage,
  })),
)

const RiskProfilePage = lazy(() =>
  import('@/features/profile/pages/RiskProfilePage').then((module) => ({
    default: module.RiskProfilePage,
  })),
)

const SimulationDetailPage = lazy(() =>
  import('@/features/simulation/pages/SimulationDetailPage').then((module) => ({
    default: module.SimulationDetailPage,
  })),
)

const SimulationsPage = lazy(() =>
  import('@/features/simulation/pages/SimulationsPage').then((module) => ({
    default: module.SimulationsPage,
  })),
)

const ReportingPage = lazy(() =>
  import('@/features/reporting/pages/ReportingPage').then((module) => ({
    default: module.ReportingPage,
  })),
)

const AssetReportPage = lazy(() =>
  import('@/features/reporting/pages/AssetReportPage').then((module) => ({
    default: module.AssetReportPage,
  })),
)

const PortfolioReportPage = lazy(() =>
  import('@/features/reporting/pages/PortfolioReportPage').then((module) => ({
    default: module.PortfolioReportPage,
  })),
)

const SimulationReportPage = lazy(() =>
  import('@/features/reporting/pages/SimulationReportPage').then((module) => ({
    default: module.SimulationReportPage,
  })),
)

const ForbiddenPage = lazy(() =>
  import('@/pages/ForbiddenPage').then((module) => ({
    default: module.ForbiddenPage,
  })),
)

const HomePage = lazy(() =>
  import('@/pages/HomePage').then((module) => ({
    default: module.HomePage,
  })),
)

const LoginPage = lazy(() =>
  import('@/pages/LoginPage').then((module) => ({
    default: module.LoginPage,
  })),
)

const RegisterPage = lazy(() =>
  import('@/pages/RegisterPage').then((module) => ({
    default: module.RegisterPage,
  })),
)

export function AppRouter() {
  return (
    <Suspense fallback={<PageLoadingState />}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<ApplicationLayout />}>
            <Route path="/app" element={<DashboardPage />} />
            <Route path="/app/profile" element={<RiskProfilePage />} />

            <Route element={<PermissionRoute requiredPermissions={['activos.leer']} />}>
              <Route path="/app/market" element={<MarketPage />} />
              <Route path="/app/market/assets/:assetId" element={<AssetDetailPage />} />
            </Route>

            <Route element={<PermissionRoute requiredPermissions={['trabajos.leer']} />}>
              <Route path="/app/market/synchronizations" element={<MarketSynchronizationsPage />} />
              <Route
                path="/app/market/synchronizations/:executionId"
                element={<MarketSynchronizationDetailPage />}
              />
            </Route>

            <Route element={<PermissionRoute requiredPermissions={['portafolios.leer']} />}>
              <Route path="/app/portfolios" element={<PortfoliosPage />} />
              <Route path="/app/portfolios/:portfolioId" element={<PortfolioDetailPage />} />
            </Route>

            <Route element={<PermissionRoute requiredPermissions={['simulaciones.leer']} />}>
              <Route path="/app/simulations" element={<SimulationsPage />} />
              <Route path="/app/simulations/:configurationId" element={<SimulationDetailPage />} />
            </Route>

            <Route
              element={<PermissionRoute requiredPermissions={['analisis.leer', 'activos.leer']} />}
            >
              <Route path="/app/ai" element={<AiAnalysisPage />} />
            </Route>

            <Route
              element={<PermissionRoute requiredPermissions={['noticias.leer', 'activos.leer']} />}
            >
              <Route path="/app/news" element={<NewsPage />} />
            </Route>

            <Route element={<PermissionRoute requiredPermissions={['notificaciones.leer']} />}>
              <Route path="/app/notifications" element={<NotificationsPage />} />
              <Route
                path="/app/notifications/:notificationId"
                element={<NotificationDetailPage />}
              />
            </Route>

            <Route element={<PermissionRoute requiredPermissions={['reportes.leer']} />}>
              <Route path="/app/reports" element={<ReportingPage />} />
              <Route path="/app/reports/assets" element={<AssetReportPage />} />
              <Route path="/app/reports/portfolios" element={<PortfolioReportPage />} />
              <Route path="/app/reports/simulations" element={<SimulationReportPage />} />
            </Route>

            <Route
              element={
                <AnyPermissionRoute
                  requiredPermissions={['reportes.administrar', 'notificaciones.administrar']}
                />
              }
            >
              <Route path="/app/admin" element={<AdminPage />} />
            </Route>

            <Route element={<PermissionRoute requiredPermissions={['reportes.administrar']} />}>
              <Route path="/app/admin/users" element={<AdminUsersPage />} />
              <Route path="/app/admin/audit" element={<AdminAuditPage />} />
              <Route path="/app/admin/jobs" element={<AdminJobsPage />} />
            </Route>

            <Route
              element={<PermissionRoute requiredPermissions={['notificaciones.administrar']} />}
            >
              <Route path="/app/admin/notifications" element={<AdminNotificationsPage />} />
            </Route>

            <Route path="/forbidden" element={<ForbiddenPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
