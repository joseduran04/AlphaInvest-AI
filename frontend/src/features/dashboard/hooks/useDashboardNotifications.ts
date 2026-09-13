import { useQuery } from '@tanstack/react-query'

import { dashboardNotificationsRequest } from '@/features/dashboard/api/dashboardApi'
import { dashboardQueryKeys } from '@/features/dashboard/hooks/dashboardQueryKeys'

export function useDashboardNotifications(enabled = true) {
  return useQuery({
    queryKey: dashboardQueryKeys.notifications(),
    queryFn: dashboardNotificationsRequest,
    enabled,
  })
}
