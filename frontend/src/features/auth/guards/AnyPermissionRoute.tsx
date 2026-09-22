import { Navigate, Outlet } from 'react-router'

import { useAuth } from '@/features/auth/hooks/useAuth'

interface AnyPermissionRouteProps {
  requiredPermissions: string[]
}

export function AnyPermissionRoute({ requiredPermissions }: AnyPermissionRouteProps) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const hasAnyRequiredPermission = requiredPermissions.some((permission) =>
    user.permisos.includes(permission),
  )

  if (!hasAnyRequiredPermission) {
    return <Navigate to="/forbidden" replace />
  }

  return <Outlet />
}
