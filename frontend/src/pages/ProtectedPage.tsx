import { useAuth } from '@/features/auth/hooks/useAuth'

export function ProtectedPage() {
  const { user, logout } = useAuth()

  return (
    <main>
      <h1>Sesión autenticada</h1>

      <p>
        {user?.nombres} {user?.apellidos}
      </p>

      <p>{user?.correo}</p>

      <button type="button" onClick={() => void logout()}>
        Cerrar sesión
      </button>
    </main>
  )
}
