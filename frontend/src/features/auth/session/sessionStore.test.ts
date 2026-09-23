import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  clearSessionTokens,
  getAccessToken,
  getAccessTokenExpiresAt,
  getRefreshToken,
  setSessionTokens,
} from './sessionStore'

const REFRESH_TOKEN_STORAGE_KEY = 'alphainvest.refresh_token'

describe('sessionStore', () => {
  beforeEach(() => {
    clearSessionTokens()
    window.sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    clearSessionTokens()
    window.sessionStorage.clear()
  })

  it('almacena los tokens y persiste únicamente el refresh token', () => {
    vi.spyOn(Date, 'now').mockReturnValue(1_000)

    setSessionTokens({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 3600,
    })

    expect(getAccessToken()).toBe('access-token')
    expect(getRefreshToken()).toBe('refresh-token')
    expect(getAccessTokenExpiresAt()).toBe(3_601_000)
    expect(window.sessionStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)).toBe('refresh-token')
  })

  it('recupera el refresh token desde sessionStorage', async () => {
    window.sessionStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, 'stored-refresh-token')

    vi.resetModules()

    const isolatedStore = await import('./sessionStore')

    expect(isolatedStore.getRefreshToken()).toBe('stored-refresh-token')

    isolatedStore.clearSessionTokens()
  })

  it('limpia tokens en memoria y sessionStorage', () => {
    setSessionTokens({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 60,
    })

    clearSessionTokens()

    expect(getAccessToken()).toBeNull()
    expect(getRefreshToken()).toBeNull()
    expect(getAccessTokenExpiresAt()).toBeNull()
    expect(window.sessionStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)).toBeNull()
  })

  it('mantiene los tokens en memoria si sessionStorage falla al escribir', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('storage unavailable')
    })

    setSessionTokens({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 60,
    })

    expect(getAccessToken()).toBe('access-token')
    expect(getRefreshToken()).toBe('refresh-token')
    expect(getAccessTokenExpiresAt()).not.toBeNull()
  })
})
