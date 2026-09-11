import { Navigate, Outlet } from 'react-router'

import { useAuth } from '@/features/auth/hooks/useAuth'

interface PermissionRouteProps {
  requiredPermissions: string[]
}

export function PermissionRoute({ requiredPermissions }: PermissionRouteProps) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const hasRequiredPermissions = requiredPermissions.every((permission) =>
    user.permisos.includes(permission),
  )

  if (!hasRequiredPermissions) {
    return <Navigate to="/forbidden" replace />
  }

  return <Outlet />
}
