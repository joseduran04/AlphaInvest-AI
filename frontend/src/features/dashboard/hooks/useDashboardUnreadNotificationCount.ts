import { useQuery } from '@tanstack/react-query'

import { dashboardUnreadNotificationCountRequest } from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardUnreadNotificationCount(enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.unreadNotificationCount(),
    queryFn: dashboardUnreadNotificationCountRequest,
    enabled,
  })
}
