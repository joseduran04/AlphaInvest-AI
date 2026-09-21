import { Link } from 'react-router'

import type { NotificationResponse } from '@/api/types'

interface NotificationCardProps {
  notification: NotificationResponse
}

function formatNotificationDate(value: string): string {
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatNotificationLabel(value: string): string {
  return value
    .toLowerCase()
    .replaceAll('_', ' ')
    .replace(/(^|\s)\S/g, (character) => character.toUpperCase())
}

export function NotificationCard({ notification }: NotificationCardProps) {
  const isUnread = notification.read_at === null

  return (
    <article className={`notification-card${isUnread ? ' notification-card--unread' : ''}`}>
      <header className="notification-card__header">
        <div className="notification-card__heading">
          <div className="notification-card__type">
            <span>{formatNotificationLabel(notification.type)}</span>

            {isUnread ? (
              <span className="notification-card__unread-indicator">No leída</span>
            ) : (
              <span className="notification-card__read-indicator">Leída</span>
            )}
          </div>

          <h3>{notification.title}</h3>
        </div>

        <span
          className={`notification-priority notification-priority--${notification.priority.toLowerCase()}`}
        >
          {formatNotificationLabel(notification.priority)}
        </span>
      </header>

      <p className="notification-card__message">{notification.message}</p>

      <footer className="notification-card__footer">
        <div>
          <span>Recibida</span>
          <strong>{formatNotificationDate(notification.sent_at ?? notification.created_at)}</strong>
        </div>

        {notification.read_at ? (
          <div>
            <span>Leída</span>
            <strong>{formatNotificationDate(notification.read_at)}</strong>
          </div>
        ) : null}

        <Link
          className="button button--secondary notification-card__detail-link"
          to={`/app/notifications/${notification.id}`}
        >
          Ver detalle
        </Link>
      </footer>
    </article>
  )
}
