import type { TokenResponse } from '@/api/types'

const REFRESH_TOKEN_STORAGE_KEY = 'alphainvest.refresh_token'

let accessToken: string | null = null
let refreshToken: string | null = null
let accessTokenExpiresAt: number | null = null

function readStoredRefreshToken(): string | null {
  try {
    return window.sessionStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

function writeStoredRefreshToken(token: string): void {
  try {
    window.sessionStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, token)
  } catch {
    // La sesión permanece disponible en memoria aunque sessionStorage falle.
  }
}

function removeStoredRefreshToken(): void {
  try {
    window.sessionStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
  } catch {
    // No hay acción adicional posible si sessionStorage no está disponible.
  }
}

export function getAccessToken(): string | null {
  return accessToken
}

export function getRefreshToken(): string | null {
  if (refreshToken) {
    return refreshToken
  }

  refreshToken = readStoredRefreshToken()

  return refreshToken
}

export function getAccessTokenExpiresAt(): number | null {
  return accessTokenExpiresAt
}

export function setSessionTokens(tokens: TokenResponse): void {
  accessToken = tokens.access_token
  refreshToken = tokens.refresh_token
  accessTokenExpiresAt = Date.now() + tokens.expires_in * 1_000

  writeStoredRefreshToken(tokens.refresh_token)
}

export function clearSessionTokens(): void {
  accessToken = null
  refreshToken = null
  accessTokenExpiresAt = null

  removeStoredRefreshToken()
}
