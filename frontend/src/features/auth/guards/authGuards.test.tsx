import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { AuthContextValue } from '@/features/auth/context/AuthContext'
import { AnyPermissionRoute } from '@/features/auth/guards/AnyPermissionRoute'
import { PermissionRoute } from '@/features/auth/guards/PermissionRoute'
import { ProtectedRoute } from '@/features/auth/guards/ProtectedRoute'
import { useAuth } from '@/features/auth/hooks/useAuth'

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}))

const mockedUseAuth = vi.mocked(useAuth)

const baseAuthValue: AuthContextValue = {
  user: {
    id: '00000000-0000-0000-0000-000000000001',
    nombres: 'Usuario',
    apellidos: 'Prueba',
    correo: 'usuario@prueba.com',
    estado: 'ACTIVO',
    correo_verificado: true,
    roles: ['INVERSIONISTA'],
    permisos: ['portafolios.leer', 'simulaciones.leer'],
  },
  status: 'authenticated',
  error: null,
  isAuthenticated: true,
  login: vi.fn(),
  logout: vi.fn(),
  restore: vi.fn(),
  hasPermission: vi.fn(),
}

function LocationStateProbe() {
  const location = useLocation()
  const state = location.state as { from?: { pathname?: string } } | null

  return (
    <div>
      <span data-testid="current-path">{location.pathname}</span>
      <span data-testid="from-path">{state?.from?.pathname ?? ''}</span>
    </div>
  )
}

function renderProtectedRoute(initialPath = '/private') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/private" element={<div>Contenido protegido</div>} />
        </Route>

        <Route
          path="/login"
          element={
            <>
              <div>Página de login</div>
              <LocationStateProbe />
            </>
          }
        />
      </Routes>
    </MemoryRouter>,
  )
}

function renderPermissionRoute(requiredPermissions: string[]) {
  return render(
    <MemoryRouter initialEntries={['/restricted']}>
      <Routes>
        <Route element={<PermissionRoute requiredPermissions={requiredPermissions} />}>
          <Route path="/restricted" element={<div>Contenido autorizado</div>} />
        </Route>

        <Route path="/login" element={<div>Página de login</div>} />
        <Route path="/forbidden" element={<div>Acceso prohibido</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

function renderAnyPermissionRoute(requiredPermissions: string[]) {
  return render(
    <MemoryRouter initialEntries={['/restricted']}>
      <Routes>
        <Route element={<AnyPermissionRoute requiredPermissions={requiredPermissions} />}>
          <Route path="/restricted" element={<div>Contenido autorizado</div>} />
        </Route>

        <Route path="/login" element={<div>Página de login</div>} />
        <Route path="/forbidden" element={<div>Acceso prohibido</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    mockedUseAuth.mockReturnValue(baseAuthValue)
  })

  it('muestra el estado de carga mientras se verifica la sesión', () => {
    mockedUseAuth.mockReturnValue({
      ...baseAuthValue,
      user: null,
      status: 'checking',
      isAuthenticated: false,
    })

    renderProtectedRoute()

    expect(screen.getByText('Validando sesión...')).toBeInTheDocument()
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument()
  })

  it('muestra el estado de error cuando falla la comprobación de sesión', () => {
    mockedUseAuth.mockReturnValue({
      ...baseAuthValue,
      user: null,
      status: 'error',
      error: new Error('Error de autenticación'),
      isAuthenticated: false,
    })

    renderProtectedRoute()

    expect(
      screen.getByRole('heading', { name: 'No fue posible validar la sesión' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Error de autenticación')).toBeInTheDocument()
    expect(screen.queryByText('Contenido protegido')).not.toBeInTheDocument()
  })

  it('redirige al login conservando la ubicación solicitada cuando no está autenticado', () => {
    mockedUseAuth.mockReturnValue({
      ...baseAuthValue,
      user: null,
      status: 'unauthenticated',
      isAuthenticated: false,
    })

    renderProtectedRoute()

    expect(screen.getByText('Página de login')).toBeInTheDocument()
    expect(screen.getByTestId('current-path')).toHaveTextContent('/login')
    expect(screen.getByTestId('from-path')).toHaveTextContent('/private')
  })

  it('renderiza la ruta hija cuando el usuario está autenticado', () => {
    renderProtectedRoute()

    expect(screen.getByText('Contenido protegido')).toBeInTheDocument()
  })
})

describe('PermissionRoute', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    mockedUseAuth.mockReturnValue(baseAuthValue)
  })

  it('redirige al login cuando no existe usuario', () => {
    mockedUseAuth.mockReturnValue({
      ...baseAuthValue,
      user: null,
      status: 'unauthenticated',
      isAuthenticated: false,
    })

    renderPermissionRoute(['portafolios.leer'])

    expect(screen.getByText('Página de login')).toBeInTheDocument()
  })

  it('permite acceso cuando el usuario posee todos los permisos requeridos', () => {
    renderPermissionRoute(['portafolios.leer', 'simulaciones.leer'])

    expect(screen.getByText('Contenido autorizado')).toBeInTheDocument()
  })

  it('redirige a forbidden cuando falta al menos un permiso requerido', () => {
    renderPermissionRoute(['portafolios.leer', 'reportes.administrar'])

    expect(screen.getByText('Acceso prohibido')).toBeInTheDocument()
  })
})

describe('AnyPermissionRoute', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    mockedUseAuth.mockReturnValue(baseAuthValue)
  })

  it('redirige al login cuando no existe usuario', () => {
    mockedUseAuth.mockReturnValue({
      ...baseAuthValue,
      user: null,
      status: 'unauthenticated',
      isAuthenticated: false,
    })

    renderAnyPermissionRoute(['portafolios.leer'])

    expect(screen.getByText('Página de login')).toBeInTheDocument()
  })

  it('permite acceso cuando el usuario posee al menos uno de los permisos requeridos', () => {
    renderAnyPermissionRoute(['reportes.administrar', 'portafolios.leer'])

    expect(screen.getByText('Contenido autorizado')).toBeInTheDocument()
  })

  it('redirige a forbidden cuando no posee ninguno de los permisos requeridos', () => {
    renderAnyPermissionRoute(['reportes.administrar', 'notificaciones.administrar'])

    expect(screen.getByText('Acceso prohibido')).toBeInTheDocument()
  })
})
