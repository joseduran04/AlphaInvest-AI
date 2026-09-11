import { Link } from 'react-router'

export function ForbiddenPage() {
  return (
    <main>
      <section>
        <h1>Acceso no autorizado</h1>

        <p>No tienes los permisos necesarios para acceder a esta sección.</p>

        <Link to="/app">Volver</Link>
      </section>
    </main>
  )
}
