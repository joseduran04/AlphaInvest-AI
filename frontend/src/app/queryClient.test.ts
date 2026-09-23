import { describe, expect, it } from 'vitest'

import { ApiError } from '@/api/errors'

import { queryClient } from './queryClient'

function getQueryRetry() {
  const retry = queryClient.getDefaultOptions().queries?.retry

  if (typeof retry !== 'function') {
    throw new Error('La política de retry de queries no está configurada como función')
  }

  return retry
}

describe('queryClient', () => {
  const retry = getQueryRetry()

  it('reintenta errores de red mientras no se alcance el límite', () => {
    const error = new ApiError({
      kind: 'network',
      message: 'Error de red',
    })

    expect(retry(0, error)).toBe(true)
    expect(retry(1, error)).toBe(true)
  })

  it('reintenta errores de timeout mientras no se alcance el límite', () => {
    const error = new ApiError({
      kind: 'timeout',
      message: 'Timeout',
    })

    expect(retry(0, error)).toBe(true)
    expect(retry(1, error)).toBe(true)
  })

  it('reintenta errores HTTP 5xx', () => {
    const error = new ApiError({
      kind: 'http',
      status: 503,
      message: 'Servicio no disponible',
    })

    expect(retry(0, error)).toBe(true)
  })

  it('no reintenta errores HTTP 4xx', () => {
    const error = new ApiError({
      kind: 'http',
      status: 404,
      message: 'No encontrado',
    })

    expect(retry(0, error)).toBe(false)
  })

  it('no reintenta errores HTTP sin status', () => {
    const error = new ApiError({
      kind: 'http',
      message: 'Error HTTP',
    })

    expect(retry(0, error)).toBe(false)
  })

  it('no reintenta errores que no sean ApiError', () => {
    expect(retry(0, new Error('Error genérico'))).toBe(false)
  })

  it('detiene los reintentos al alcanzar el límite configurado', () => {
    const error = new ApiError({
      kind: 'network',
      message: 'Error de red',
    })

    expect(retry(2, error)).toBe(false)
    expect(retry(3, error)).toBe(false)
  })

  it('mantiene deshabilitados los reintentos de mutations', () => {
    expect(queryClient.getDefaultOptions().mutations?.retry).toBe(false)
  })

  it('mantiene la configuración base de caché y refetch', () => {
    const queries = queryClient.getDefaultOptions().queries

    expect(queries?.staleTime).toBe(30_000)
    expect(queries?.gcTime).toBe(5 * 60_000)
    expect(queries?.refetchOnWindowFocus).toBe(false)
  })
})
