import { Navigate, Route, Routes } from 'react-router'

import { PermissionRoute } from '@/features/auth/guards/PermissionRoute'
import { ProtectedRoute } from '@/features/auth/guards/ProtectedRoute'
import { AiAnalysisPage } from '@/features/ai/pages/AiAnalysisPage'
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage'
import { AssetDetailPage } from '@/features/market/pages/AssetDetailPage'
import { MarketPage } from '@/features/market/pages/MarketPage'
import { MarketSynchronizationDetailPage } from '@/features/market/pages/MarketSynchronizationDetailPage'
import { MarketSynchronizationsPage } from '@/features/market/pages/MarketSynchronizationsPage'
import { NewsPage } from '@/features/news/pages/NewsPage'
import { NotificationDetailPage } from '@/features/notifications/pages/NotificationDetailPage'
import { NotificationsPage } from '@/features/notifications/pages/NotificationsPage'
import { PortfolioDetailPage } from '@/features/portfolio/pages/PortfolioDetailPage'
import { PortfoliosPage } from '@/features/portfolio/pages/PortfoliosPage'
import { RiskProfilePage } from '@/features/profile/pages/RiskProfilePage'
import { SimulationDetailPage } from '@/features/simulation/pages/SimulationDetailPage'
import { SimulationsPage } from '@/features/simulation/pages/SimulationsPage'
import { ReportingPage } from '@/features/reporting/pages/ReportingPage'
import { AssetReportPage } from '@/features/reporting/pages/AssetReportPage'
import { PortfolioReportPage } from '@/features/reporting/pages/PortfolioReportPage'
import { SimulationReportPage } from '@/features/reporting/pages/SimulationReportPage'
import { RecommendationReportPage } from '@/features/reporting/pages/RecommendationReportPage'
import { ApplicationLayout } from '@/layouts/ApplicationLayout'
import { ForbiddenPage } from '@/pages/ForbiddenPage'
import { HomePage } from '@/pages/HomePage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'

export function AppRouter() {
  return (
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
            <Route path="/app/notifications/:notificationId" element={<NotificationDetailPage />} />
          </Route>

          <Route element={<PermissionRoute requiredPermissions={['reportes.leer']} />}>
            <Route path="/app/reports" element={<ReportingPage />} />
            <Route path="/app/reports/assets" element={<AssetReportPage />} />
            <Route path="/app/reports/portfolios" element={<PortfolioReportPage />} />
            <Route path="/app/reports/simulations" element={<SimulationReportPage />} />
            <Route path="/app/reports/recommendations" element={<RecommendationReportPage />} />
          </Route>

          <Route path="/forbidden" element={<ForbiddenPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
