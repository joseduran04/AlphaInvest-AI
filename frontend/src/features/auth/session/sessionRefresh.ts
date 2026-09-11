import axios from 'axios'

import { normalizeApiError } from '@/api/errors'
import type { RefreshRequest, TokenResponse } from '@/api/types'
import { notifySessionInvalidated } from '@/features/auth/session/sessionEvents'
import { env } from '@/lib/env'

import { clearSessionTokens, getRefreshToken, setSessionTokens } from './sessionStore'

const REFRESH_PATH = '/api/v1/auth/refresh'

const refreshClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15_000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

let refreshPromise: Promise<string> | null = null

export async function refreshSession(): Promise<string> {
  if (refreshPromise) {
    return refreshPromise
  }

  const refreshToken = getRefreshToken()

  if (!refreshToken) {
    clearSessionTokens()
    notifySessionInvalidated()

    throw new Error('Refresh token no disponible')
  }

  refreshPromise = (async () => {
    try {
      const payload: RefreshRequest = {
        refresh_token: refreshToken,
      }

      const response = await refreshClient.post<TokenResponse>(REFRESH_PATH, payload)

      setSessionTokens(response.data)

      return response.data.access_token
    } catch (error) {
      const apiError = normalizeApiError(error)

      if (apiError.kind === 'http' && apiError.status === 401) {
        clearSessionTokens()
        notifySessionInvalidated()
      }

      throw apiError
    } finally {
      refreshPromise = null
    }
  })()

  return refreshPromise
}
