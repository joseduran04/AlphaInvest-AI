import { Navigate, Route, Routes } from 'react-router'

import { ProtectedRoute } from '@/features/auth/guards/ProtectedRoute'
import { RiskProfilePage } from '@/features/profile/pages/RiskProfilePage'
import { ApplicationLayout } from '@/layouts/ApplicationLayout'
import { ForbiddenPage } from '@/pages/ForbiddenPage'
import { HomePage } from '@/pages/HomePage'
import { LoginPage } from '@/pages/LoginPage'
import { ProtectedPage } from '@/pages/ProtectedPage'
import { RegisterPage } from '@/pages/RegisterPage'

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<ApplicationLayout />}>
          <Route path="/app" element={<ProtectedPage />} />
          <Route path="/app/profile" element={<RiskProfilePage />} />
          <Route path="/forbidden" element={<ForbiddenPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
