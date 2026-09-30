import { Link, Navigate } from 'react-router'

import { AuthLoadingState } from '@/features/auth/components/AuthLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'

export function HomePage() {
  const { status, isAuthenticated } = useAuth()

  if (status === 'checking') {
    return <AuthLoadingState />
  }

  if (isAuthenticated) {
    return <Navigate to="/app" replace />
  }

  return (
    <main className="app">
      <section className="app__content">
        <p className="app__eyebrow">AlphaInvest AI</p>

        <h1>Plataforma inteligente para análisis e inversión educativa</h1>

        <p className="app__description">
          Consulta precios reales, simula inversiones con datos históricos y analiza el tono de las
          noticias financieras con inteligencia artificial.
        </p>

        <div className="app__actions">
          <Link className="button button--primary" to="/login">
            Iniciar sesión
          </Link>
          <Link className="button button--secondary" to="/register">
            Crear cuenta
          </Link>
        </div>

        <p className="app__disclaimer">
          Herramienta educativa: no constituye asesoría financiera ni garantiza rendimientos.
        </p>
      </section>
    </main>
  )
}
