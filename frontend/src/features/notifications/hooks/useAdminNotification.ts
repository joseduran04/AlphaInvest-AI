import { useQuery } from '@tanstack/react-query'

import { adminNotificationRequest } from '@/features/notifications/api/notificationsApi'
import { notificationQueryKeys } from '@/features/notifications/hooks/notificationQueryKeys'

export function useAdminNotification(notificationId: string, enabled = true) {
  return useQuery({
    queryKey: notificationQueryKeys.adminDetail(notificationId),
    queryFn: () => adminNotificationRequest(notificationId),
    enabled: enabled && notificationId.length > 0,
  })
}
