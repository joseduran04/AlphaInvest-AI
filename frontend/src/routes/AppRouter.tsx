import { Navigate, Route, Routes } from 'react-router'

import { ProtectedRoute } from '@/features/auth/guards/ProtectedRoute'
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
        <Route path="/app" element={<ProtectedPage />} />
        <Route path="/forbidden" element={<ForbiddenPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
