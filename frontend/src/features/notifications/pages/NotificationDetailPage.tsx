import { Link, useParams } from 'react-router'

import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useMarkNotificationRead } from '@/features/notifications/hooks/useMarkNotificationRead'
import { useNotification } from '@/features/notifications/hooks/useNotification'

import '@/styles/notifications.css'

function formatDateTime(value: string | null): string {
  if (!value) {
    return 'No disponible'
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatLabel(value: string): string {
  return value
    .toLowerCase()
    .replaceAll('_', ' ')
    .replace(/(^|\s)\S/g, (character) => character.toUpperCase())
}

function formatData(data: { [key: string]: unknown } | null): string {
  if (!data) {
    return 'No disponible'
  }

  return JSON.stringify(data, null, 2)
}

export function NotificationDetailPage() {
  const { notificationId = '' } = useParams<{ notificationId: string }>()
  const { hasPermission } = useAuth()

  const canReadNotifications = hasPermission('notificaciones.leer')
  const notificationQuery = useNotification(notificationId, canReadNotifications)
  const markReadMutation = useMarkNotificationRead(notificationId)

  if (!canReadNotifications) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar esta notificación."
      />
    )
  }

  if (!notificationId) {
    return (
      <PageErrorState
        title="Notificación no válida"
        message="No se recibió un identificador de notificación válido."
      />
    )
  }

  if (notificationQuery.isPending) {
    return <PageLoadingState message="Cargando detalle de notificación..." />
  }

  if (notificationQuery.isError) {
    return (
      <PageErrorState
        title="No fue posible cargar la notificación"
        message={notificationQuery.error.message}
        onRetry={() => {
          void notificationQuery.refetch()
        }}
      />
    )
  }

  const notification = notificationQuery.data
  const isUnread = notification.read_at === null

  function handleMarkAsRead() {
    if (!isUnread || markReadMutation.isPending) {
      return
    }

    markReadMutation.mutate()
  }

  return (
    <section className="notification-detail">
      <header className="notification-detail__header">
        <div>
          <p className="app__eyebrow">Notificaciones · Detalle</p>
          <h1>{notification.title}</h1>
          <p className="app__description">Información registrada para esta notificación.</p>
        </div>

        <Link className="button button--secondary" to="/app/notifications">
          Volver a notificaciones
        </Link>
      </header>

      <section className="notification-detail__panel">
        <header className="notification-detail__section-header">
          <div>
            <p className="notifications-results__eyebrow">Notificación</p>
            <h2>Información general</h2>
          </div>

          <div className="notification-detail__badges">
            <span
              className={`notification-priority notification-priority--${notification.priority.toLowerCase()}`}
            >
              {formatLabel(notification.priority)}
            </span>

            <span
              className={isUnread ? 'notification-detail__unread' : 'notification-detail__read'}
            >
              {isUnread ? 'No leída' : 'Leída'}
            </span>
          </div>
        </header>

        <p className="notification-detail__message">{notification.message}</p>

        <dl className="notification-detail__grid">
          <div>
            <dt>ID</dt>
            <dd>{notification.id}</dd>
          </div>

          <div>
            <dt>Tipo</dt>
            <dd>{formatLabel(notification.type)}</dd>
          </div>

          <div>
            <dt>Canal</dt>
            <dd>{formatLabel(notification.channel)}</dd>
          </div>

          <div>
            <dt>Estado</dt>
            <dd>{formatLabel(notification.status)}</dd>
          </div>

          <div>
            <dt>Creada</dt>
            <dd>{formatDateTime(notification.created_at)}</dd>
          </div>

          <div>
            <dt>Programada</dt>
            <dd>{formatDateTime(notification.scheduled_at)}</dd>
          </div>

          <div>
            <dt>Enviada</dt>
            <dd>{formatDateTime(notification.sent_at)}</dd>
          </div>

          <div>
            <dt>Leída</dt>
            <dd>{formatDateTime(notification.read_at)}</dd>
          </div>

          <div>
            <dt>Tipo de referencia</dt>
            <dd>{notification.reference_type ?? 'No disponible'}</dd>
          </div>

          <div>
            <dt>Referencia</dt>
            <dd>{notification.reference_id ?? 'No disponible'}</dd>
          </div>
        </dl>
      </section>

      <section className="notification-detail__panel">
        <header className="notification-detail__section-header">
          <div>
            <p className="notifications-results__eyebrow">Datos</p>
            <h2>Información asociada</h2>
          </div>
        </header>

        <pre className="notification-detail__data">{formatData(notification.data)}</pre>
      </section>

      {isUnread ? (
        <section className="notification-detail__actions">
          <button
            className="button button--primary"
            type="button"
            disabled={markReadMutation.isPending}
            onClick={handleMarkAsRead}
          >
            {markReadMutation.isPending ? 'Marcando...' : 'Marcar como leída'}
          </button>

          {markReadMutation.isError ? (
            <p className="notification-detail__action-error" role="alert">
              {markReadMutation.error.message}
            </p>
          ) : null}
        </section>
      ) : null}
    </section>
  )
}
