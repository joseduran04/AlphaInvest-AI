import { useQueryClient } from '@tanstack/react-query'
import { type PropsWithChildren, useCallback, useEffect, useMemo, useState } from 'react'

import { ApiError } from '@/api/errors'
import type { LoginRequest, UserResponse } from '@/api/types'
import { subscribeToSessionInvalidation } from '@/features/auth/session/sessionEvents'
import { loginSession, logoutSession, restoreSession } from '@/features/auth/session/sessionService'

import { AuthContext, type AuthContextValue, type AuthStatus } from './AuthContext'

function toError(error: unknown): Error {
  if (error instanceof Error) {
    return error
  }

  return new Error('Ocurrió un error desconocido durante la autenticación')
}

function isInvalidSessionError(error: Error): boolean {
  return error instanceof ApiError && error.kind === 'http' && error.status === 401
}

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient()

  const [user, setUser] = useState<UserResponse | null>(null)
  const [status, setStatus] = useState<AuthStatus>('checking')
  const [error, setError] = useState<Error | null>(null)

  const invalidateAuthenticatedState = useCallback((): void => {
    queryClient.clear()
    setUser(null)
    setError(null)
    setStatus('unauthenticated')
  }, [queryClient])

  const applyRestoreSuccess = useCallback((restoredUser: UserResponse | null): void => {
    setError(null)

    if (!restoredUser) {
      setUser(null)
      setStatus('unauthenticated')
      return
    }

    setUser(restoredUser)
    setStatus('authenticated')
  }, [])

  const applyRestoreError = useCallback(
    (restoreError: unknown): void => {
      const normalizedError = toError(restoreError)

      setUser(null)

      if (isInvalidSessionError(normalizedError)) {
        invalidateAuthenticatedState()
        return
      }

      setError(normalizedError)
      setStatus('error')
    },
    [invalidateAuthenticatedState],
  )

  const restore = useCallback(async (): Promise<void> => {
    setStatus('checking')
    setError(null)

    try {
      const restoredUser = await restoreSession()
      applyRestoreSuccess(restoredUser)
    } catch (restoreError) {
      applyRestoreError(restoreError)
    }
  }, [applyRestoreError, applyRestoreSuccess])

  const login = useCallback(
    async (data: LoginRequest): Promise<UserResponse> => {
      setError(null)

      try {
        const authenticatedUser = await loginSession(data)

        queryClient.clear()
        setUser(authenticatedUser)
        setStatus('authenticated')

        return authenticatedUser
      } catch (loginError) {
        const normalizedError = toError(loginError)

        setUser(null)
        setError(normalizedError)
        setStatus('unauthenticated')

        throw normalizedError
      }
    },
    [queryClient],
  )

  const logout = useCallback(async (): Promise<void> => {
    setError(null)

    try {
      await logoutSession()
    } finally {
      invalidateAuthenticatedState()
    }
  }, [invalidateAuthenticatedState])

  const hasPermission = useCallback(
    (permission: string): boolean => user?.permisos.includes(permission) ?? false,
    [user],
  )

  useEffect(() => {
    return subscribeToSessionInvalidation(invalidateAuthenticatedState)
  }, [invalidateAuthenticatedState])

  useEffect(() => {
    let cancelled = false

    async function initializeSession(): Promise<void> {
      try {
        const restoredUser = await restoreSession()

        if (!cancelled) {
          applyRestoreSuccess(restoredUser)
        }
      } catch (restoreError) {
        if (!cancelled) {
          applyRestoreError(restoreError)
        }
      }
    }

    void initializeSession()

    return () => {
      cancelled = true
    }
  }, [applyRestoreError, applyRestoreSuccess])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      status,
      error,
      isAuthenticated: status === 'authenticated' && user !== null,
      login,
      logout,
      restore,
      hasPermission,
    }),
    [error, hasPermission, login, logout, restore, status, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
