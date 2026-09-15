import { Navigate, Route, Routes } from 'react-router'

import { PermissionRoute } from '@/features/auth/guards/PermissionRoute'
import { ProtectedRoute } from '@/features/auth/guards/ProtectedRoute'
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage'
import { AssetDetailPage } from '@/features/market/pages/AssetDetailPage'
import { MarketPage } from '@/features/market/pages/MarketPage'
import { MarketSynchronizationDetailPage } from '@/features/market/pages/MarketSynchronizationDetailPage'
import { MarketSynchronizationsPage } from '@/features/market/pages/MarketSynchronizationsPage'
import { PortfolioDetailPage } from '@/features/portfolio/pages/PortfolioDetailPage'
import { PortfoliosPage } from '@/features/portfolio/pages/PortfoliosPage'
import { RiskProfilePage } from '@/features/profile/pages/RiskProfilePage'
import { SimulationsPage } from '@/features/simulation/pages/SimulationsPage'
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
          </Route>

          <Route path="/forbidden" element={<ForbiddenPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
