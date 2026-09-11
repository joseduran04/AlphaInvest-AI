import { useAuth } from '@/features/auth/hooks/useAuth'

export function AuthErrorState() {
  const { error, restore } = useAuth()

  return (
    <main>
      <h1>No fue posible validar la sesión</h1>

      <p>{error?.message ?? 'Ocurrió un error al comunicarse con el servidor.'}</p>

      <button type="button" onClick={() => void restore()}>
        Reintentar
      </button>
    </main>
  )
}
