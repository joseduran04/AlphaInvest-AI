import { apiClient } from '@/api/client'
import type {
  NotificationListQuery,
  NotificationListResponse,
  NotificationResponse,
  UnreadNotificationCountResponse,
} from '@/api/types'

const NOTIFICATIONS_PATH = '/api/v1/notifications'

export async function notificationsRequest(
  params: NotificationListQuery = {},
): Promise<NotificationListResponse> {
  const response = await apiClient.get<NotificationListResponse>(NOTIFICATIONS_PATH, {
    params,
  })

  return response.data
}

export async function unreadNotificationCountRequest(): Promise<UnreadNotificationCountResponse> {
  const response = await apiClient.get<UnreadNotificationCountResponse>(
    `${NOTIFICATIONS_PATH}/unread-count`,
  )

  return response.data
}

export async function notificationRequest(notificationId: string): Promise<NotificationResponse> {
  const response = await apiClient.get<NotificationResponse>(
    `${NOTIFICATIONS_PATH}/${notificationId}`,
  )

  return response.data
}

export async function markNotificationReadRequest(
  notificationId: string,
): Promise<NotificationResponse> {
  const response = await apiClient.patch<NotificationResponse>(
    `${NOTIFICATIONS_PATH}/${notificationId}/read`,
  )

  return response.data
}
