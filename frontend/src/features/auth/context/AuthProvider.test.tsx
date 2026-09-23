import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, render, screen, waitFor } from '@testing-library/react'
import { useContext, useEffect } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/api/errors'
import type { LoginRequest, UserResponse } from '@/api/types'
import { AuthContext } from '@/features/auth/context/AuthContext'
import { AuthProvider } from '@/features/auth/context/AuthProvider'
import { subscribeToSessionInvalidation } from '@/features/auth/session/sessionEvents'
import { loginSession, logoutSession, restoreSession } from '@/features/auth/session/sessionService'

vi.mock('@/features/auth/session/sessionService', () => ({
  loginSession: vi.fn(),
  logoutSession: vi.fn(),
  restoreSession: vi.fn(),
}))

vi.mock('@/features/auth/session/sessionEvents', () => ({
  subscribeToSessionInvalidation: vi.fn(),
}))

const mockedLoginSession = vi.mocked(loginSession)
const mockedLogoutSession = vi.mocked(logoutSession)
const mockedRestoreSession = vi.mocked(restoreSession)
const mockedSubscribeToSessionInvalidation = vi.mocked(subscribeToSessionInvalidation)

const loginData: LoginRequest = {
  correo: 'usuario@prueba.com',
  password: 'password-de-prueba',
}

const user: UserResponse = {
  id: '00000000-0000-0000-0000-000000000001',
  nombres: 'Usuario',
  apellidos: 'Prueba',
  correo: 'usuario@prueba.com',
  estado: 'ACTIVO',
  correo_verificado: true,
  roles: ['INVERSIONISTA'],
  permisos: ['portafolios.leer'],
}

let contextValue: React.ContextType<typeof AuthContext> = null
let sessionInvalidatedListener: (() => void) | null = null

function AuthConsumer() {
  const context = useContext(AuthContext)

  useEffect(() => {
    contextValue = context
  }, [context])

  return (
    <div>
      <span data-testid="status">{context?.status}</span>
      <span data-testid="authenticated">{String(context?.isAuthenticated ?? false)}</span>
      <span data-testid="email">{context?.user?.correo ?? ''}</span>
      <span data-testid="error">{context?.error?.message ?? ''}</span>
    </div>
  )
}

function renderAuthProvider() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })

  const clearSpy = vi.spyOn(queryClient, 'clear')

  render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AuthConsumer />
      </AuthProvider>
    </QueryClientProvider>,
  )

  return {
    queryClient,
    clearSpy,
  }
}

describe('AuthProvider', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    contextValue = null
    sessionInvalidatedListener = null

    mockedSubscribeToSessionInvalidation.mockImplementation((listener) => {
      sessionInvalidatedListener = listener
      return vi.fn()
    })
  })

  it('restaura un usuario autenticado al inicializar', async () => {
    mockedRestoreSession.mockResolvedValue(user)

    renderAuthProvider()

    expect(screen.getByTestId('status')).toHaveTextContent('checking')

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('authenticated')
    })

    expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    expect(screen.getByTestId('email')).toHaveTextContent(user.correo)
    expect(mockedRestoreSession).toHaveBeenCalledTimes(1)
  })

  it('queda como no autenticado cuando no existe una sesión restaurable', async () => {
    mockedRestoreSession.mockResolvedValue(null)

    renderAuthProvider()

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated')
    })

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('email')).toBeEmptyDOMElement()
  })

  it('expone estado de error cuando falla la restauración por un error no 401', async () => {
    mockedRestoreSession.mockRejectedValue(new Error('Error de red'))

    renderAuthProvider()

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('error')
    })

    expect(screen.getByTestId('error')).toHaveTextContent('Error de red')
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
  })

  it('invalida el estado autenticado cuando la restauración falla con 401', async () => {
    mockedRestoreSession.mockRejectedValue(
      new ApiError({
        kind: 'http',
        status: 401,
        message: 'Sesión inválida',
      }),
    )

    const { clearSpy } = renderAuthProvider()

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated')
    })

    expect(clearSpy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('error')).toBeEmptyDOMElement()
  })

  it('autentica al usuario y limpia las consultas después de un login correcto', async () => {
    mockedRestoreSession.mockResolvedValue(null)
    mockedLoginSession.mockResolvedValue(user)

    const { clearSpy } = renderAuthProvider()

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated')
    })

    await act(async () => {
      await contextValue?.login(loginData)
    })

    expect(mockedLoginSession).toHaveBeenCalledWith(loginData)
    expect(clearSpy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('status')).toHaveTextContent('authenticated')
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    expect(screen.getByTestId('email')).toHaveTextContent(user.correo)
  })

  it('permanece no autenticado y expone el error cuando falla el login', async () => {
    const loginError = new Error('Credenciales inválidas')

    mockedRestoreSession.mockResolvedValue(null)
    mockedLoginSession.mockRejectedValue(loginError)

    renderAuthProvider()

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated')
    })

    let loginPromise: Promise<UserResponse> | undefined

    act(() => {
      loginPromise = contextValue?.login(loginData)
    })

    await expect(loginPromise).rejects.toThrow('Credenciales inválidas')

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Credenciales inválidas')
    })

    expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated')
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
  })

  it('invalida el estado local incluso cuando falla el servicio de logout', async () => {
    mockedRestoreSession.mockResolvedValue(user)
    mockedLogoutSession.mockRejectedValue(new Error('Error de logout'))

    const { clearSpy } = renderAuthProvider()

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('authenticated')
    })

    let logoutPromise: Promise<void> | undefined

    act(() => {
      logoutPromise = contextValue?.logout()
    })

    await expect(logoutPromise).rejects.toThrow('Error de logout')

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated')
    })

    expect(clearSpy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('email')).toBeEmptyDOMElement()
  })

  it('invalida la autenticación cuando recibe el evento externo de sesión inválida', async () => {
    mockedRestoreSession.mockResolvedValue(user)

    const { clearSpy } = renderAuthProvider()

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('authenticated')
    })

    expect(sessionInvalidatedListener).not.toBeNull()

    act(() => {
      sessionInvalidatedListener?.()
    })

    expect(clearSpy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated')
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
  })

  it('consulta los permisos del usuario autenticado', async () => {
    mockedRestoreSession.mockResolvedValue(user)

    renderAuthProvider()

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('authenticated')
    })

    expect(contextValue?.hasPermission('portafolios.leer')).toBe(true)
    expect(contextValue?.hasPermission('reportes.administrar')).toBe(false)
  })
})
