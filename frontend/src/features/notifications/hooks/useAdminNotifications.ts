import { useQuery } from '@tanstack/react-query'

import type { AdminNotificationListQuery } from '@/api/types'
import { adminNotificationsRequest } from '@/features/notifications/api/notificationsApi'
import { notificationQueryKeys } from '@/features/notifications/hooks/notificationQueryKeys'

export function useAdminNotifications(params: AdminNotificationListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: notificationQueryKeys.adminList(params),
    queryFn: () => adminNotificationsRequest(params),
    enabled,
  })
}
