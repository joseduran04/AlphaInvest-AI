import { useQuery } from '@tanstack/react-query'

import type { NotificationListQuery } from '@/api/types'
import { notificationsRequest } from '@/features/notifications/api/notificationsApi'
import { notificationQueryKeys } from '@/features/notifications/hooks/notificationQueryKeys'

export function useNotifications(params: NotificationListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: notificationQueryKeys.list(params),
    queryFn: () => notificationsRequest(params),
    enabled,
  })
}
