import { useState } from 'react'

import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { NotificationCard } from '@/features/notifications/components/NotificationCard'
import { useNotifications } from '@/features/notifications/hooks/useNotifications'
import { useUnreadNotificationCount } from '@/features/notifications/hooks/useUnreadNotificationCount'

import '@/styles/notifications.css'

const PAGE_SIZE = 20

export function NotificationsPage() {
  const { hasPermission } = useAuth()
  const canReadNotifications = hasPermission('notificaciones.leer')

  const [unreadOnly, setUnreadOnly] = useState(false)
  const [page, setPage] = useState(0)

  const notificationsQuery = useNotifications(
    {
      unread_only: unreadOnly,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    },
    canReadNotifications,
  )

  const unreadCountQuery = useUnreadNotificationCount(canReadNotifications)

  if (!canReadNotifications) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar notificaciones."
      />
    )
  }

  const notifications = notificationsQuery.data?.items ?? []
  const total = notificationsQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const firstResult = total === 0 ? 0 : page * PAGE_SIZE + 1
  const lastResult = Math.min((page + 1) * PAGE_SIZE, total)

  function handleFilterChange(nextUnreadOnly: boolean) {
    setUnreadOnly(nextUnreadOnly)
    setPage(0)
  }

  function handlePageChange(nextPage: number) {
    setPage(nextPage)
  }

  return (
    <section className="notifications-page">
      <header className="notifications-page__header">
        <div>
          <p className="app__eyebrow">Notificaciones</p>
          <h1>Centro de notificaciones</h1>
          <p className="app__description">
            Consulta los avisos y eventos registrados para tu cuenta en AlphaInvest AI.
          </p>
        </div>

        {!unreadCountQuery.isPending && !unreadCountQuery.isError ? (
          <div className="notifications-summary">
            <span>No leídas</span>
            <strong>{unreadCountQuery.data.unread}</strong>
          </div>
        ) : null}
      </header>

      <section className="notifications-results">
        <header className="notifications-results__header">
          <div>
            <p className="notifications-results__eyebrow">Actividad</p>
            <h2>Notificaciones disponibles</h2>
          </div>

          {!notificationsQuery.isPending && !notificationsQuery.isError ? (
            <span className="notifications-results__count">
              {total} {total === 1 ? 'notificación' : 'notificaciones'}
            </span>
          ) : null}
        </header>

        <div className="notifications-filters" aria-label="Filtrar notificaciones">
          <button
            className={`button ${!unreadOnly ? 'button--primary' : 'button--secondary'}`}
            type="button"
            disabled={notificationsQuery.isFetching}
            onClick={() => handleFilterChange(false)}
          >
            Todas
          </button>

          <button
            className={`button ${unreadOnly ? 'button--primary' : 'button--secondary'}`}
            type="button"
            disabled={notificationsQuery.isFetching}
            onClick={() => handleFilterChange(true)}
          >
            No leídas
          </button>
        </div>

        {unreadCountQuery.isError ? (
          <div className="notifications-count-error" role="alert">
            No fue posible actualizar el contador de notificaciones no leídas.
          </div>
        ) : null}

        {notificationsQuery.isPending ? (
          <PageLoadingState message="Cargando notificaciones..." />
        ) : notificationsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar las notificaciones"
            message={notificationsQuery.error.message}
            onRetry={() => {
              void notificationsQuery.refetch()
              void unreadCountQuery.refetch()
            }}
          />
        ) : notifications.length === 0 ? (
          <PageEmptyState
            title={unreadOnly ? 'No tienes notificaciones sin leer' : 'No tienes notificaciones'}
            description={
              unreadOnly
                ? 'Todas tus notificaciones disponibles ya fueron leídas.'
                : 'Cuando AlphaInvest AI genere avisos para tu cuenta, aparecerán en este espacio.'
            }
          />
        ) : (
          <>
            <div className="notifications-feed">
              {notifications.map((notification) => (
                <NotificationCard key={notification.id} notification={notification} />
              ))}
            </div>

            <footer className="notifications-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="notifications-pagination__controls">
                <button
                  className="button button--secondary"
                  type="button"
                  disabled={page === 0 || notificationsQuery.isFetching}
                  onClick={() => handlePageChange(Math.max(0, page - 1))}
                >
                  Anterior
                </button>

                <span>
                  Página {page + 1} de {totalPages}
                </span>

                <button
                  className="button button--secondary"
                  type="button"
                  disabled={(page + 1) * PAGE_SIZE >= total || notificationsQuery.isFetching}
                  onClick={() => handlePageChange(page + 1)}
                >
                  Siguiente
                </button>
              </div>
            </footer>
          </>
        )}
      </section>
    </section>
  )
}
