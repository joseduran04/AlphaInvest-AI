import { useMutation, useQueryClient } from '@tanstack/react-query'

import { markNotificationReadRequest } from '@/features/notifications/api/notificationsApi'
import { notificationQueryKeys } from '@/features/notifications/hooks/notificationQueryKeys'

export function useMarkNotificationRead(notificationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => markNotificationReadRequest(notificationId),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: notificationQueryKeys.listsRoot(),
        }),
        queryClient.invalidateQueries({
          queryKey: notificationQueryKeys.detail(notificationId),
        }),
        queryClient.invalidateQueries({
          queryKey: notificationQueryKeys.unreadCount(),
        }),
      ])
    },
  })
}
