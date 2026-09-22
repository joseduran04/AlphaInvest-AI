import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import type { AdminNotificationListQuery, NotificationResponse } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useAdminNotification } from '@/features/notifications/hooks/useAdminNotification'
import { useAdminNotifications } from '@/features/notifications/hooks/useAdminNotifications'
import { useCancelAdminNotification } from '@/features/notifications/hooks/useCancelAdminNotification'

import '@/styles/admin.css'

const PAGE_SIZE = 20

const NOTIFICATION_STATUSES = [
  'PENDIENTE',
  'PROGRAMADA',
  'ENVIANDO',
  'ENVIADA',
  'FALLIDA',
  'CANCELADA',
] as const

const NOTIFICATION_TYPES = [
  'SISTEMA',
  'SEGURIDAD',
  'ALERTA_PRECIO',
  'SIMULACION',
  'ANALISIS_IA',
  'RECOMENDACION',
  'PORTAFOLIO',
  'MANTENIMIENTO',
  'OTRA',
] as const

const NOTIFICATION_CHANNELS = ['APLICACION', 'CORREO', 'PUSH'] as const

interface AdminNotificationFilters {
  userId: string
  status: NonNullable<AdminNotificationListQuery['status']> | ''
  type: NonNullable<AdminNotificationListQuery['type']> | ''
  channel: NonNullable<AdminNotificationListQuery['channel']> | ''
}

const initialFilters: AdminNotificationFilters = {
  userId: '',
  status: '',
  type: '',
  channel: '',
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString('es-MX')
}

function canCancelNotification(notification: NotificationResponse): boolean {
  return notification.status === 'PENDIENTE' || notification.status === 'PROGRAMADA'
}

export function AdminNotificationsPage() {
  const { hasPermission } = useAuth()

  const canManageNotifications = hasPermission('notificaciones.administrar')

  const [draftFilters, setDraftFilters] = useState<AdminNotificationFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<AdminNotificationFilters>(initialFilters)
  const [page, setPage] = useState(0)
  const [selectedNotificationId, setSelectedNotificationId] = useState('')

  const params: AdminNotificationListQuery = {
    user_id: appliedFilters.userId.trim() || undefined,
    status: appliedFilters.status || undefined,
    type: appliedFilters.type || undefined,
    channel: appliedFilters.channel || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const notificationsQuery = useAdminNotifications(params, canManageNotifications)

  const notificationDetailQuery = useAdminNotification(
    selectedNotificationId,
    canManageNotifications && selectedNotificationId.length > 0,
  )

  const cancelNotification = useCancelAdminNotification(selectedNotificationId)

  if (!canManageNotifications) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para administrar notificaciones."
      />
    )
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setAppliedFilters({
      userId: draftFilters.userId.trim(),
      status: draftFilters.status,
      type: draftFilters.type,
      channel: draftFilters.channel,
    })
    setPage(0)
  }

  function handleReset() {
    setDraftFilters(initialFilters)
    setAppliedFilters(initialFilters)
    setPage(0)
  }

  function handleCancel(notification: NotificationResponse) {
    if (!canCancelNotification(notification) || cancelNotification.isPending) {
      return
    }

    const confirmed = window.confirm(
      `¿Deseas cancelar la notificación "${notification.title}"? Esta acción no debe utilizarse si el envío ya comenzó.`,
    )

    if (!confirmed) {
      return
    }

    setSelectedNotificationId(notification.id)

    cancelNotification.mutate()
  }

  const notifications = notificationsQuery.data?.items ?? []
  const total = notificationsQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const firstResult = total === 0 ? 0 : page * PAGE_SIZE + 1
  const lastResult = Math.min((page + 1) * PAGE_SIZE, total)
  const selectedNotification = notificationDetailQuery.data

  return (
    <section className="admin-page">
      <header className="admin-page__header">
        <div>
          <p className="app__eyebrow">Administración</p>
          <h1>Notificaciones</h1>
          <p className="app__description">
            Consulta notificaciones del sistema, revisa sus detalles y cancela envíos pendientes.
          </p>
        </div>

        <Link className="button button--secondary" to="/app/admin">
          Centro de administración
        </Link>
      </header>

      <form className="admin-filters" onSubmit={handleSubmit}>
        <div className="admin-section__header">
          <div>
            <h2>Filtros</h2>
            <p>Consulta notificaciones por usuario, estado, tipo o canal.</p>
          </div>

          <button className="button button--secondary" type="button" onClick={handleReset}>
            Limpiar filtros
          </button>
        </div>

        <div className="admin-filters__grid">
          <label className="admin-field">
            <span>Usuario</span>
            <input
              type="text"
              value={draftFilters.userId}
              placeholder="UUID del usuario"
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  userId: event.target.value,
                }))
              }
            />
          </label>

          <label className="admin-field">
            <span>Estado</span>
            <select
              value={draftFilters.status}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  status: event.target.value as AdminNotificationFilters['status'],
                }))
              }
            >
              <option value="">Todos</option>
              {NOTIFICATION_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>

          <label className="admin-field">
            <span>Tipo</span>
            <select
              value={draftFilters.type}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  type: event.target.value as AdminNotificationFilters['type'],
                }))
              }
            >
              <option value="">Todos</option>
              {NOTIFICATION_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>

          <label className="admin-field">
            <span>Canal</span>
            <select
              value={draftFilters.channel}
              onChange={(event) =>
                setDraftFilters((current) => ({
                  ...current,
                  channel: event.target.value as AdminNotificationFilters['channel'],
                }))
              }
            >
              <option value="">Todos</option>
              {NOTIFICATION_CHANNELS.map((channel) => (
                <option key={channel} value={channel}>
                  {channel}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="admin-filters__actions">
          <button className="button button--primary" type="submit">
            Aplicar filtros
          </button>
        </div>
      </form>

      <section className="admin-results">
        <header className="admin-section__header">
          <div>
            <p className="admin-overview__eyebrow">Resultados</p>
            <h2>Notificaciones del sistema</h2>
          </div>

          {!notificationsQuery.isPending && !notificationsQuery.isError ? (
            <span className="admin-results__count">{total} notificaciones</span>
          ) : null}
        </header>

        {cancelNotification.isError ? (
          <p className="admin-export-error" role="alert">
            No fue posible cancelar la notificación: {cancelNotification.error.message}
          </p>
        ) : null}

        {notificationsQuery.isPending ? (
          <PageLoadingState message="Cargando notificaciones..." />
        ) : notificationsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar las notificaciones"
            message={notificationsQuery.error.message}
            onRetry={() => {
              void notificationsQuery.refetch()
            }}
          />
        ) : notifications.length === 0 ? (
          <PageEmptyState
            title="No se encontraron notificaciones"
            description="No existen notificaciones que coincidan con los filtros seleccionados."
            action={
              <button className="button button--secondary" type="button" onClick={handleReset}>
                Limpiar filtros
              </button>
            }
          />
        ) : (
          <>
            <div className="admin-table-wrapper">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Notificación</th>
                    <th>Usuario</th>
                    <th>Tipo</th>
                    <th>Canal</th>
                    <th>Estado</th>
                    <th>Prioridad</th>
                    <th>Creada</th>
                    <th>Enviada</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {notifications.map((notification) => (
                    <tr key={notification.id}>
                      <td>
                        <strong>{notification.title}</strong>
                        <span>{notification.message}</span>
                      </td>
                      <td>{notification.user_id}</td>
                      <td>{notification.type}</td>
                      <td>{notification.channel}</td>
                      <td>{notification.status}</td>
                      <td>{notification.priority}</td>
                      <td>{formatDateTime(notification.created_at)}</td>
                      <td>{formatDateTime(notification.sent_at)}</td>
                      <td>
                        <div className="admin-notification-actions">
                          <button
                            className="button button--secondary"
                            type="button"
                            onClick={() => setSelectedNotificationId(notification.id)}
                          >
                            Ver detalle
                          </button>

                          {canCancelNotification(notification) ? (
                            <button
                              className="button button--secondary"
                              type="button"
                              disabled={cancelNotification.isPending}
                              onClick={() => handleCancel(notification)}
                            >
                              {cancelNotification.isPending &&
                              selectedNotificationId === notification.id
                                ? 'Cancelando...'
                                : 'Cancelar'}
                            </button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <footer className="admin-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="admin-pagination__controls">
                <button
                  className="button button--secondary"
                  type="button"
                  disabled={page === 0}
                  onClick={() => setPage((current) => Math.max(0, current - 1))}
                >
                  Anterior
                </button>

                <span>
                  Página {page + 1} de {totalPages}
                </span>

                <button
                  className="button button--secondary"
                  type="button"
                  disabled={page + 1 >= totalPages}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Siguiente
                </button>
              </div>
            </footer>
          </>
        )}
      </section>

      {selectedNotificationId ? (
        <section className="admin-notification-detail">
          <div className="admin-section__header">
            <div>
              <p className="admin-overview__eyebrow">Detalle</p>
              <h2>Notificación seleccionada</h2>
            </div>

            <button
              className="button button--secondary"
              type="button"
              onClick={() => setSelectedNotificationId('')}
            >
              Cerrar detalle
            </button>
          </div>

          {notificationDetailQuery.isPending ? (
            <PageLoadingState message="Cargando detalle..." />
          ) : notificationDetailQuery.isError ? (
            <PageErrorState
              title="No fue posible cargar el detalle"
              message={notificationDetailQuery.error.message}
              onRetry={() => {
                void notificationDetailQuery.refetch()
              }}
            />
          ) : selectedNotification ? (
            <dl className="admin-notification-detail__grid">
              <div>
                <dt>ID</dt>
                <dd>{selectedNotification.id}</dd>
              </div>
              <div>
                <dt>Usuario</dt>
                <dd>{selectedNotification.user_id}</dd>
              </div>
              <div>
                <dt>Estado</dt>
                <dd>{selectedNotification.status}</dd>
              </div>
              <div>
                <dt>Tipo</dt>
                <dd>{selectedNotification.type}</dd>
              </div>
              <div>
                <dt>Canal</dt>
                <dd>{selectedNotification.channel}</dd>
              </div>
              <div>
                <dt>Prioridad</dt>
                <dd>{selectedNotification.priority}</dd>
              </div>
              <div>
                <dt>Programada</dt>
                <dd>{formatDateTime(selectedNotification.scheduled_at)}</dd>
              </div>
              <div>
                <dt>Enviada</dt>
                <dd>{formatDateTime(selectedNotification.sent_at)}</dd>
              </div>
              <div>
                <dt>Leída</dt>
                <dd>{formatDateTime(selectedNotification.read_at)}</dd>
              </div>
              <div>
                <dt>Intentos de entrega</dt>
                <dd>{selectedNotification.delivery_attempts}</dd>
              </div>
              <div>
                <dt>Referencia</dt>
                <dd>
                  {selectedNotification.reference_type ?? 'No disponible'} /{' '}
                  {selectedNotification.reference_id ?? 'No disponible'}
                </dd>
              </div>
              <div>
                <dt>Último error</dt>
                <dd>{selectedNotification.last_error ?? 'Sin errores registrados'}</dd>
              </div>
            </dl>
          ) : null}
        </section>
      ) : null}
    </section>
  )
}
