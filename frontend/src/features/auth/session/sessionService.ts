import type { LoginRequest, LogoutRequest, UserResponse } from '@/api/types'
import { currentUserRequest, loginRequest, logoutRequest } from '@/features/auth/api/authApi'

import { refreshSession } from './sessionRefresh'
import { clearSessionTokens, getRefreshToken, setSessionTokens } from './sessionStore'

export async function loginSession(data: LoginRequest): Promise<UserResponse> {
  const tokens = await loginRequest(data)

  setSessionTokens(tokens)

  try {
    return await currentUserRequest()
  } catch (error) {
    clearSessionTokens()
    throw error
  }
}

export async function restoreSession(): Promise<UserResponse | null> {
  if (!getRefreshToken()) {
    return null
  }

  await refreshSession()

  return currentUserRequest()
}

export async function logoutSession(): Promise<void> {
  const refreshToken = getRefreshToken()

  if (!refreshToken) {
    clearSessionTokens()
    return
  }

  const payload: LogoutRequest = {
    refresh_token: refreshToken,
  }

  try {
    await logoutRequest(payload)
  } finally {
    clearSessionTokens()
  }
}
