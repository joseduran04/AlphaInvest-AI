import { useQuery } from '@tanstack/react-query'

import { notificationRequest } from '@/features/notifications/api/notificationsApi'
import { notificationQueryKeys } from '@/features/notifications/hooks/notificationQueryKeys'

export function useNotification(notificationId: string, enabled = true) {
  return useQuery({
    queryKey: notificationQueryKeys.detail(notificationId),
    queryFn: () => notificationRequest(notificationId),
    enabled: enabled && notificationId.length > 0,
  })
}
