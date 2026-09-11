import { useAuth } from '@/features/auth/hooks/useAuth'

export function ProtectedPage() {
  const { user } = useAuth()

  return (
    <section>
      <p className="app__eyebrow">Panel principal</p>

      <h1>Bienvenido, {user?.nombres}</h1>

      <p className="app__description">
        Desde este espacio podrás acceder progresivamente a las herramientas de análisis, mercado,
        portafolios, simulación e inteligencia artificial de AlphaInvest AI.
      </p>
    </section>
  )
}
