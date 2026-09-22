import type { AdminNotificationListQuery, NotificationListQuery } from '@/api/types'

export const notificationQueryKeys = {
  all: ['notifications'] as const,

  listsRoot: () => [...notificationQueryKeys.all, 'list'] as const,

  list: (params: NotificationListQuery) => [...notificationQueryKeys.listsRoot(), params] as const,

  detailsRoot: () => [...notificationQueryKeys.all, 'detail'] as const,

  detail: (notificationId: string) =>
    [...notificationQueryKeys.detailsRoot(), notificationId] as const,

  unreadCount: () => [...notificationQueryKeys.all, 'unread-count'] as const,

  adminRoot: () => [...notificationQueryKeys.all, 'admin'] as const,

  adminListsRoot: () => [...notificationQueryKeys.adminRoot(), 'list'] as const,

  adminList: (params: AdminNotificationListQuery = {}) =>
    [...notificationQueryKeys.adminListsRoot(), params] as const,

  adminDetailsRoot: () => [...notificationQueryKeys.adminRoot(), 'detail'] as const,

  adminDetail: (notificationId: string) =>
    [...notificationQueryKeys.adminDetailsRoot(), notificationId] as const,
}
