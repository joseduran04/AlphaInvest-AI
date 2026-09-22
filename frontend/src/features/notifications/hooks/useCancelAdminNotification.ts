import { useMutation, useQueryClient } from '@tanstack/react-query'

import { cancelAdminNotificationRequest } from '@/features/notifications/api/notificationsApi'
import { notificationQueryKeys } from '@/features/notifications/hooks/notificationQueryKeys'

export function useCancelAdminNotification(notificationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => cancelAdminNotificationRequest(notificationId),

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: notificationQueryKeys.adminListsRoot(),
        }),
        queryClient.invalidateQueries({
          queryKey: notificationQueryKeys.adminDetail(notificationId),
        }),
      ])
    },
  })
}
