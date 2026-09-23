import axios from 'axios'
import { describe, expect, it } from 'vitest'

import { ApiError, normalizeApiError } from './errors'

describe('normalizeApiError', () => {
  it('conserva una instancia ApiError existente', () => {
    const error = new ApiError({
      kind: 'http',
      status: 409,
      message: 'Conflicto',
    })

    expect(normalizeApiError(error)).toBe(error)
  })

  it('normaliza errores desconocidos', () => {
    const cause = new Error('fallo inesperado')

    const result = normalizeApiError(cause)

    expect(result).toBeInstanceOf(ApiError)
    expect(result.kind).toBe('unknown')
    expect(result.message).toBe('Ocurrió un error inesperado')
    expect(result.cause).toBe(cause)
  })

  it('normaliza timeouts de Axios', () => {
    const cause = new axios.AxiosError('timeout', 'ECONNABORTED')

    const result = normalizeApiError(cause)

    expect(result.kind).toBe('timeout')
    expect(result.message).toBe('La solicitud tardó demasiado tiempo en responder')
  })

  it('normaliza errores de red sin respuesta HTTP', () => {
    const cause = new axios.AxiosError('Network Error', 'ERR_NETWORK')

    const result = normalizeApiError(cause)

    expect(result.kind).toBe('network')
    expect(result.message).toBe('No fue posible conectar con el servidor')
  })

  it('normaliza el envelope de error de AlphaInvest', () => {
    const cause = new axios.AxiosError('Request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
      data: {
        success: false,
        error: {
          code: 'portfolio_conflict',
          message: 'El portafolio no puede cerrarse',
          details: {
            positions: 2,
          },
        },
        meta: {
          request_id: 'request-123',
        },
      },
      status: 409,
      statusText: 'Conflict',
      headers: {},
      config: {
        headers: new axios.AxiosHeaders(),
      },
    })

    const result = normalizeApiError(cause)

    expect(result.kind).toBe('http')
    expect(result.status).toBe(409)
    expect(result.code).toBe('portfolio_conflict')
    expect(result.message).toBe('El portafolio no puede cerrarse')
    expect(result.details).toEqual({
      positions: 2,
    })
    expect(result.requestId).toBe('request-123')
  })

  it('normaliza errores FastAPI con detail de texto', () => {
    const cause = new axios.AxiosError('Request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
      data: {
        detail: 'Credenciales inválidas',
      },
      status: 401,
      statusText: 'Unauthorized',
      headers: {},
      config: {
        headers: new axios.AxiosHeaders(),
      },
    })

    const result = normalizeApiError(cause)

    expect(result.kind).toBe('http')
    expect(result.status).toBe(401)
    expect(result.message).toBe('Credenciales inválidas')
  })

  it('utiliza el mensaje HTTP de respaldo cuando la respuesta no tiene un formato conocido', () => {
    const cause = new axios.AxiosError('Request failed', 'ERR_BAD_RESPONSE', undefined, undefined, {
      data: {},
      status: 403,
      statusText: 'Forbidden',
      headers: {},
      config: {
        headers: new axios.AxiosHeaders(),
      },
    })

    const result = normalizeApiError(cause)

    expect(result.kind).toBe('http')
    expect(result.status).toBe(403)
    expect(result.message).toBe('No tienes permisos para realizar esta acción')
  })
})
