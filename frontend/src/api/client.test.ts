import axios, {
  AxiosHeaders,
  type AxiosAdapter,
  type AxiosError,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/api/errors'

const { getAccessTokenMock, refreshSessionMock } = vi.hoisted(() => ({
  getAccessTokenMock: vi.fn(),
  refreshSessionMock: vi.fn(),
}))

vi.mock('@/features/auth/session/sessionStore', () => ({
  getAccessToken: getAccessTokenMock,
}))

vi.mock('@/features/auth/session/sessionRefresh', () => ({
  refreshSession: refreshSessionMock,
}))

import { apiClient, publicApiClient } from './client'

function createResponse(
  config: InternalAxiosRequestConfig,
  status: number,
  data: unknown,
): AxiosResponse {
  return {
    data,
    status,
    statusText: String(status),
    headers: {},
    config,
  }
}

function createAxiosError(status: number, config: InternalAxiosRequestConfig): AxiosError {
  return new axios.AxiosError(
    `HTTP ${status}`,
    undefined,
    config,
    undefined,
    createResponse(config, status, {}),
  )
}

describe('api client', () => {
  beforeEach(() => {
    getAccessTokenMock.mockReset()
    refreshSessionMock.mockReset()
  })

  it('configura los clientes con timeout y headers base', () => {
    expect(publicApiClient.defaults.timeout).toBe(15_000)
    expect(apiClient.defaults.timeout).toBe(15_000)

    expect(AxiosHeaders.from(publicApiClient.defaults.headers).get('Accept')).toBe(
      'application/json',
    )

    expect(AxiosHeaders.from(apiClient.defaults.headers).get('Content-Type')).toBe(
      'application/json',
    )
  })

  it('envía la petición sin Authorization cuando no existe access token', async () => {
    getAccessTokenMock.mockReturnValue(null)

    const adapter = vi.fn<AxiosAdapter>(async (config) => createResponse(config, 200, { ok: true }))

    const response = await apiClient.get('/api/v1/test', {
      adapter,
    })

    expect(response.data).toEqual({ ok: true })
    expect(adapter).toHaveBeenCalledTimes(1)

    const config = adapter.mock.calls[0]?.[0]

    expect(AxiosHeaders.from(config?.headers).get('Authorization')).toBeUndefined()
  })

  it('agrega Authorization Bearer cuando existe access token', async () => {
    getAccessTokenMock.mockReturnValue('current-access-token')

    const adapter = vi.fn<AxiosAdapter>(async (config) => createResponse(config, 200, { ok: true }))

    await apiClient.get('/api/v1/test', {
      adapter,
    })

    const config = adapter.mock.calls[0]?.[0]

    expect(AxiosHeaders.from(config?.headers).get('Authorization')).toBe(
      'Bearer current-access-token',
    )
  })

  it('devuelve correctamente una respuesta exitosa del cliente público', async () => {
    const adapter: AxiosAdapter = async (config) => createResponse(config, 200, { public: true })

    const response = await publicApiClient.get('/api/v1/public', {
      adapter,
    })

    expect(response.status).toBe(200)
    expect(response.data).toEqual({ public: true })
  })

  it('normaliza un error no Axios del cliente público', async () => {
    const adapter: AxiosAdapter = async () => {
      throw new Error('Error inesperado')
    }

    await expect(
      publicApiClient.get('/api/v1/public', {
        adapter,
      }),
    ).rejects.toMatchObject({
      kind: 'unknown',
      message: 'Ocurrió un error inesperado',
    })
  })

  it('normaliza un error no Axios del cliente autenticado', async () => {
    const adapter: AxiosAdapter = async () => {
      throw new Error('Error inesperado')
    }

    await expect(
      apiClient.get('/api/v1/test', {
        adapter,
      }),
    ).rejects.toMatchObject({
      kind: 'unknown',
      message: 'Ocurrió un error inesperado',
    })

    expect(refreshSessionMock).not.toHaveBeenCalled()
  })

  it('no intenta refresh cuando el error HTTP es distinto de 401', async () => {
    getAccessTokenMock.mockReturnValue('current-access-token')

    const adapter: AxiosAdapter = async (config) => {
      throw createAxiosError(500, config)
    }

    await expect(
      apiClient.get('/api/v1/test', {
        adapter,
      }),
    ).rejects.toMatchObject({
      kind: 'http',
      status: 500,
    })

    expect(refreshSessionMock).not.toHaveBeenCalled()
  })

  it('renueva la sesión y reintenta una petición autenticada después de 401', async () => {
    getAccessTokenMock
      .mockReturnValueOnce('expired-access-token')
      .mockReturnValue('new-access-token')

    refreshSessionMock.mockResolvedValue('new-access-token')

    let requestCount = 0

    const adapter = vi.fn<AxiosAdapter>(async (config) => {
      requestCount += 1

      if (requestCount === 1) {
        throw createAxiosError(401, config)
      }

      return createResponse(config, 200, { ok: true })
    })

    const response = await apiClient.get('/api/v1/test', {
      adapter,
    })

    expect(response.status).toBe(200)
    expect(response.data).toEqual({ ok: true })

    expect(refreshSessionMock).toHaveBeenCalledTimes(1)
    expect(adapter).toHaveBeenCalledTimes(2)

    const retriedConfig = adapter.mock.calls[1]?.[0]

    expect(AxiosHeaders.from(retriedConfig?.headers).get('Authorization')).toBe(
      'Bearer new-access-token',
    )
  })

  it('no intenta refresh para un 401 cuando la petición no llevaba Bearer token', async () => {
    getAccessTokenMock.mockReturnValue(null)

    const adapter: AxiosAdapter = async (config) => {
      throw createAxiosError(401, config)
    }

    await expect(
      apiClient.get('/api/v1/test', {
        adapter,
      }),
    ).rejects.toMatchObject({
      kind: 'http',
      status: 401,
    })

    expect(refreshSessionMock).not.toHaveBeenCalled()
  })

  it('no ejecuta un segundo refresh cuando el reintento vuelve a responder 401', async () => {
    getAccessTokenMock
      .mockReturnValueOnce('expired-access-token')
      .mockReturnValue('new-access-token')

    refreshSessionMock.mockResolvedValue('new-access-token')

    const adapter = vi.fn<AxiosAdapter>(async (config) => {
      throw createAxiosError(401, config)
    })

    await expect(
      apiClient.get('/api/v1/test', {
        adapter,
      }),
    ).rejects.toMatchObject({
      kind: 'http',
      status: 401,
    })

    expect(adapter).toHaveBeenCalledTimes(2)
    expect(refreshSessionMock).toHaveBeenCalledTimes(1)
  })

  it('elimina Authorization del reintento si después del refresh no existe access token', async () => {
    getAccessTokenMock.mockReturnValueOnce('expired-access-token').mockReturnValue(null)

    refreshSessionMock.mockResolvedValue('refreshed-access-token')

    let requestCount = 0

    const adapter = vi.fn<AxiosAdapter>(async (config) => {
      requestCount += 1

      if (requestCount === 1) {
        throw createAxiosError(401, config)
      }

      return createResponse(config, 200, { ok: true })
    })

    await apiClient.get('/api/v1/test', {
      adapter,
    })

    expect(refreshSessionMock).toHaveBeenCalledTimes(1)
    expect(adapter).toHaveBeenCalledTimes(2)

    const retriedConfig = adapter.mock.calls[1]?.[0]

    expect(AxiosHeaders.from(retriedConfig?.headers).get('Authorization')).toBeUndefined()
  })

  it('normaliza y propaga el error cuando falla el refresh', async () => {
    getAccessTokenMock.mockReturnValue('expired-access-token')

    refreshSessionMock.mockRejectedValue(
      new ApiError({
        kind: 'network',
        message: 'No fue posible renovar la sesión',
      }),
    )

    const adapter: AxiosAdapter = async (config) => {
      throw createAxiosError(401, config)
    }

    await expect(
      apiClient.get('/api/v1/test', {
        adapter,
      }),
    ).rejects.toMatchObject({
      kind: 'network',
      message: 'No fue posible renovar la sesión',
    })

    expect(refreshSessionMock).toHaveBeenCalledTimes(1)
  })
})
