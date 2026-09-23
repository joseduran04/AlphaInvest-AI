import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { LoginRequest, TokenResponse, UserResponse } from '@/api/types'
import { currentUserRequest, loginRequest, logoutRequest } from '@/features/auth/api/authApi'

import { refreshSession } from './sessionRefresh'
import { clearSessionTokens, getRefreshToken, setSessionTokens } from './sessionStore'
import { loginSession, logoutSession, restoreSession } from './sessionService'

vi.mock('@/features/auth/api/authApi', () => ({
  currentUserRequest: vi.fn(),
  loginRequest: vi.fn(),
  logoutRequest: vi.fn(),
}))

vi.mock('./sessionRefresh', () => ({
  refreshSession: vi.fn(),
}))

vi.mock('./sessionStore', () => ({
  clearSessionTokens: vi.fn(),
  getRefreshToken: vi.fn(),
  setSessionTokens: vi.fn(),
}))

const mockedCurrentUserRequest = vi.mocked(currentUserRequest)
const mockedLoginRequest = vi.mocked(loginRequest)
const mockedLogoutRequest = vi.mocked(logoutRequest)
const mockedRefreshSession = vi.mocked(refreshSession)
const mockedClearSessionTokens = vi.mocked(clearSessionTokens)
const mockedGetRefreshToken = vi.mocked(getRefreshToken)
const mockedSetSessionTokens = vi.mocked(setSessionTokens)

const loginData: LoginRequest = {
  correo: 'usuario@prueba.com',
  password: 'password-de-prueba',
}

const tokens: TokenResponse = {
  access_token: 'access-token',
  refresh_token: 'refresh-token',
  token_type: 'bearer',
  expires_in: 900,
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

describe('sessionService', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  describe('loginSession', () => {
    it('guarda los tokens y obtiene el usuario autenticado', async () => {
      mockedLoginRequest.mockResolvedValue(tokens)
      mockedCurrentUserRequest.mockResolvedValue(user)

      await expect(loginSession(loginData)).resolves.toBe(user)

      expect(mockedLoginRequest).toHaveBeenCalledWith(loginData)
      expect(mockedSetSessionTokens).toHaveBeenCalledWith(tokens)
      expect(mockedCurrentUserRequest).toHaveBeenCalledTimes(1)
      expect(mockedClearSessionTokens).not.toHaveBeenCalled()
    })

    it('limpia los tokens cuando falla la consulta del usuario', async () => {
      const error = new Error('No fue posible consultar el usuario')

      mockedLoginRequest.mockResolvedValue(tokens)
      mockedCurrentUserRequest.mockRejectedValue(error)

      await expect(loginSession(loginData)).rejects.toBe(error)

      expect(mockedSetSessionTokens).toHaveBeenCalledWith(tokens)
      expect(mockedClearSessionTokens).toHaveBeenCalledTimes(1)
    })
  })

  describe('restoreSession', () => {
    it('retorna null cuando no existe refresh token', async () => {
      mockedGetRefreshToken.mockReturnValue(null)

      await expect(restoreSession()).resolves.toBeNull()

      expect(mockedRefreshSession).not.toHaveBeenCalled()
      expect(mockedCurrentUserRequest).not.toHaveBeenCalled()
    })

    it('renueva la sesión y obtiene el usuario cuando existe refresh token', async () => {
      mockedGetRefreshToken.mockReturnValue('refresh-token')
      mockedRefreshSession.mockResolvedValue('new-access-token')
      mockedCurrentUserRequest.mockResolvedValue(user)

      await expect(restoreSession()).resolves.toBe(user)

      expect(mockedRefreshSession).toHaveBeenCalledTimes(1)
      expect(mockedCurrentUserRequest).toHaveBeenCalledTimes(1)
    })
  })

  describe('logoutSession', () => {
    it('limpia la sesión local sin llamar a la API cuando no existe refresh token', async () => {
      mockedGetRefreshToken.mockReturnValue(null)

      await logoutSession()

      expect(mockedLogoutRequest).not.toHaveBeenCalled()
      expect(mockedClearSessionTokens).toHaveBeenCalledTimes(1)
    })

    it('envía el refresh token y limpia la sesión después del logout', async () => {
      mockedGetRefreshToken.mockReturnValue('refresh-token')
      mockedLogoutRequest.mockResolvedValue(undefined)

      await logoutSession()

      expect(mockedLogoutRequest).toHaveBeenCalledWith({
        refresh_token: 'refresh-token',
      })
      expect(mockedClearSessionTokens).toHaveBeenCalledTimes(1)
    })

    it('limpia la sesión incluso cuando la API de logout falla', async () => {
      const error = new Error('Error de logout')

      mockedGetRefreshToken.mockReturnValue('refresh-token')
      mockedLogoutRequest.mockRejectedValue(error)

      await expect(logoutSession()).rejects.toBe(error)

      expect(mockedClearSessionTokens).toHaveBeenCalledTimes(1)
    })
  })
})
