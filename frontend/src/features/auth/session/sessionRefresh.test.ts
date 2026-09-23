import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/api/errors'
import type { TokenResponse } from '@/api/types'

const {
  postMock,
  getRefreshTokenMock,
  setSessionTokensMock,
  clearSessionTokensMock,
  notifySessionInvalidatedMock,
} = vi.hoisted(() => ({
  postMock: vi.fn(),
  getRefreshTokenMock: vi.fn(),
  setSessionTokensMock: vi.fn(),
  clearSessionTokensMock: vi.fn(),
  notifySessionInvalidatedMock: vi.fn(),
}))

vi.mock('axios', async (importOriginal) => {
  const actual = await importOriginal<typeof import('axios')>()

  return {
    ...actual,
    default: {
      ...actual.default,
      create: vi.fn(() => ({
        post: postMock,
      })),
    },
  }
})

vi.mock('./sessionStore', () => ({
  getRefreshToken: getRefreshTokenMock,
  setSessionTokens: setSessionTokensMock,
  clearSessionTokens: clearSessionTokensMock,
}))

vi.mock('./sessionEvents', () => ({
  notifySessionInvalidated: notifySessionInvalidatedMock,
}))

import { refreshSession } from './sessionRefresh'

const refreshedTokens: TokenResponse = {
  access_token: 'new-access-token',
  refresh_token: 'new-refresh-token',
  token_type: 'bearer',
  expires_in: 900,
}

describe('refreshSession', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renueva la sesión y guarda los nuevos tokens', async () => {
    getRefreshTokenMock.mockReturnValue('current-refresh-token')
    postMock.mockResolvedValue({
      data: refreshedTokens,
    })

    await expect(refreshSession()).resolves.toBe('new-access-token')

    expect(postMock).toHaveBeenCalledWith('/api/v1/auth/refresh', {
      refresh_token: 'current-refresh-token',
    })
    expect(setSessionTokensMock).toHaveBeenCalledWith(refreshedTokens)
    expect(clearSessionTokensMock).not.toHaveBeenCalled()
    expect(notifySessionInvalidatedMock).not.toHaveBeenCalled()
  })

  it('limpia e invalida la sesión cuando no existe refresh token', async () => {
    getRefreshTokenMock.mockReturnValue(null)

    await expect(refreshSession()).rejects.toThrow('Refresh token no disponible')

    expect(postMock).not.toHaveBeenCalled()
    expect(clearSessionTokensMock).toHaveBeenCalledTimes(1)
    expect(notifySessionInvalidatedMock).toHaveBeenCalledTimes(1)
    expect(setSessionTokensMock).not.toHaveBeenCalled()
  })

  it('limpia e invalida la sesión cuando el refresh responde 401', async () => {
    getRefreshTokenMock.mockReturnValue('expired-refresh-token')

    postMock.mockRejectedValue(
      new ApiError({
        kind: 'http',
        status: 401,
        message: 'La sesión no es válida o ha expirado',
      }),
    )

    await expect(refreshSession()).rejects.toMatchObject({
      kind: 'http',
      status: 401,
    })

    expect(clearSessionTokensMock).toHaveBeenCalledTimes(1)
    expect(notifySessionInvalidatedMock).toHaveBeenCalledTimes(1)
    expect(setSessionTokensMock).not.toHaveBeenCalled()
  })

  it('propaga un error no 401 sin invalidar la sesión', async () => {
    getRefreshTokenMock.mockReturnValue('current-refresh-token')

    postMock.mockRejectedValue(
      new ApiError({
        kind: 'http',
        status: 500,
        message: 'Ocurrió un error interno',
      }),
    )

    await expect(refreshSession()).rejects.toMatchObject({
      kind: 'http',
      status: 500,
    })

    expect(clearSessionTokensMock).not.toHaveBeenCalled()
    expect(notifySessionInvalidatedMock).not.toHaveBeenCalled()
    expect(setSessionTokensMock).not.toHaveBeenCalled()
  })

  it('comparte una sola petición de refresh entre llamadas concurrentes', async () => {
    getRefreshTokenMock.mockReturnValue('current-refresh-token')

    let resolveRequest: ((value: { data: TokenResponse }) => void) | undefined

    postMock.mockImplementation(
      () =>
        new Promise<{ data: TokenResponse }>((resolve) => {
          resolveRequest = resolve
        }),
    )

    const firstRefresh = refreshSession()
    const secondRefresh = refreshSession()
    const thirdRefresh = refreshSession()

    expect(postMock).toHaveBeenCalledTimes(1)

    if (!resolveRequest) {
      throw new Error('La petición de refresh no fue inicializada')
    }

    resolveRequest({
      data: refreshedTokens,
    })

    await expect(Promise.all([firstRefresh, secondRefresh, thirdRefresh])).resolves.toEqual([
      'new-access-token',
      'new-access-token',
      'new-access-token',
    ])

    expect(postMock).toHaveBeenCalledTimes(1)
    expect(setSessionTokensMock).toHaveBeenCalledTimes(1)
    expect(setSessionTokensMock).toHaveBeenCalledWith(refreshedTokens)
  })
})
