import { Navigate, Outlet, useLocation } from 'react-router'

import { AuthErrorState } from '@/features/auth/components/AuthErrorState'
import { AuthLoadingState } from '@/features/auth/components/AuthLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'

export function ProtectedRoute() {
  const { status, isAuthenticated } = useAuth()
  const location = useLocation()

  if (status === 'checking') {
    return <AuthLoadingState />
  }

  if (status === 'error') {
    return <AuthErrorState />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}
