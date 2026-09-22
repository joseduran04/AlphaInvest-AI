import { Link } from 'react-router'

import { useAuth } from '@/features/auth/hooks/useAuth'
import '@/styles/admin.css'

export function AdminPage() {
  const { hasPermission } = useAuth()

  const canManageReports = hasPermission('reportes.administrar')
  const canManageNotifications = hasPermission('notificaciones.administrar')

  return (
    <section className="admin-page">
      <header className="admin-page__header">
        <div>
          <p className="app__eyebrow">Administración</p>
          <h1>Centro de administración</h1>
          <p className="app__description">
            Consulta información administrativa, auditoría, operación y notificaciones según los
            permisos asignados a tu usuario.
          </p>
        </div>
      </header>

      <section className="admin-overview">
        <header className="admin-overview__header">
          <div>
            <p className="admin-overview__eyebrow">Herramientas administrativas</p>
            <h2>Áreas disponibles</h2>
            <p>Selecciona una herramienta para consultar la información correspondiente.</p>
          </div>
        </header>

        <div className="admin-cards">
          {canManageReports && (
            <>
              <article className="admin-card">
                <div className="admin-card__content">
                  <h3>Usuarios</h3>
                  <p>
                    Consulta estado, accesos, bloqueos y roles asociados a los usuarios registrados.
                  </p>
                </div>

                <Link className="admin-card__link" to="/app/admin/users">
                  Consultar usuarios
                </Link>
              </article>

              <article className="admin-card">
                <div className="admin-card__content">
                  <h3>Auditoría</h3>
                  <p>
                    Revisa eventos consolidados por entidad, acción, origen y periodo de actividad.
                  </p>
                </div>

                <Link className="admin-card__link" to="/app/admin/audit">
                  Consultar auditoría
                </Link>
              </article>

              <article className="admin-card">
                <div className="admin-card__content">
                  <h3>Trabajos programados</h3>
                  <p>
                    Supervisa configuración, ejecuciones, resultados y estado operativo de los
                    trabajos.
                  </p>
                </div>

                <Link className="admin-card__link" to="/app/admin/jobs">
                  Consultar trabajos
                </Link>
              </article>
            </>
          )}

          {canManageNotifications && (
            <article className="admin-card">
              <div className="admin-card__content">
                <h3>Notificaciones</h3>
                <p>
                  Consulta notificaciones de forma administrativa y gestiona aquellas que todavía
                  pueden cancelarse.
                </p>
              </div>

              <Link className="admin-card__link" to="/app/admin/notifications">
                Administrar notificaciones
              </Link>
            </article>
          )}
        </div>
      </section>
    </section>
  )
}
