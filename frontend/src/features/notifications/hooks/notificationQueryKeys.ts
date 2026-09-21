import type { NotificationListQuery } from '@/api/types'

export const notificationQueryKeys = {
  all: ['notifications'] as const,

  listsRoot: () => [...notificationQueryKeys.all, 'list'] as const,

  list: (params: NotificationListQuery) => [...notificationQueryKeys.listsRoot(), params] as const,

  detailsRoot: () => [...notificationQueryKeys.all, 'detail'] as const,

  detail: (notificationId: string) =>
    [...notificationQueryKeys.detailsRoot(), notificationId] as const,

  unreadCount: () => [...notificationQueryKeys.all, 'unread-count'] as const,
}
