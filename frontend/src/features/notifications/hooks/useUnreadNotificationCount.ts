import { useQuery } from '@tanstack/react-query'

import { unreadNotificationCountRequest } from '@/features/notifications/api/notificationsApi'
import { notificationQueryKeys } from '@/features/notifications/hooks/notificationQueryKeys'

export function useUnreadNotificationCount(enabled = true) {
  return useQuery({
    queryKey: notificationQueryKeys.unreadCount(),
    queryFn: unreadNotificationCountRequest,
    enabled,
  })
}
