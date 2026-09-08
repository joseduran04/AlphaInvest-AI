import axios from 'axios'

export type ApiErrorKind = 'http' | 'network' | 'timeout' | 'unknown'

export interface ApiErrorOptions {
  kind: ApiErrorKind
  message: string
  status?: number
  code?: string
  details?: unknown
  requestId?: string | null
  cause?: unknown
}

export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number
  readonly code?: string
  readonly details?: unknown
  readonly requestId?: string | null

  constructor({ kind, message, status, code, details, requestId, cause }: ApiErrorOptions) {
    super(message, { cause })

    this.name = 'ApiError'
    this.kind = kind
    this.status = status
    this.code = code
    this.details = details
    this.requestId = requestId
  }
}

interface AlphaInvestErrorEnvelope {
  success: false
  error: {
    code: string
    message: string
    details: unknown
  }
  meta: {
    request_id: string | null
  }
}

interface FastApiErrorPayload {
  detail: unknown
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function isAlphaInvestErrorEnvelope(value: unknown): value is AlphaInvestErrorEnvelope {
  if (!isRecord(value) || value.success !== false) {
    return false
  }

  const error = value.error
  const meta = value.meta

  if (!isRecord(error) || !isRecord(meta)) {
    return false
  }

  return (
    typeof error.code === 'string' &&
    typeof error.message === 'string' &&
    'details' in error &&
    (typeof meta.request_id === 'string' || meta.request_id === null)
  )
}

function isFastApiErrorPayload(value: unknown): value is FastApiErrorPayload {
  return isRecord(value) && 'detail' in value
}

function getFastApiMessage(detail: unknown): string | undefined {
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  return undefined
}

function getHttpFallbackMessage(status?: number): string {
  switch (status) {
    case 400:
      return 'La solicitud no es válida'
    case 401:
      return 'La sesión no es válida o ha expirado'
    case 403:
      return 'No tienes permisos para realizar esta acción'
    case 404:
      return 'El recurso solicitado no fue encontrado'
    case 409:
      return 'La solicitud entra en conflicto con el estado actual'
    case 422:
      return 'Los datos enviados no son válidos'
    case 500:
      return 'Ocurrió un error interno'
    default:
      return 'La solicitud no pudo completarse'
  }
}

export function normalizeApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error
  }

  if (!axios.isAxiosError(error)) {
    return new ApiError({
      kind: 'unknown',
      message: 'Ocurrió un error inesperado',
      cause: error,
    })
  }

  if (error.code === 'ECONNABORTED') {
    return new ApiError({
      kind: 'timeout',
      message: 'La solicitud tardó demasiado tiempo en responder',
      cause: error,
    })
  }

  if (!error.response) {
    return new ApiError({
      kind: 'network',
      message: 'No fue posible conectar con el servidor',
      cause: error,
    })
  }

  const status = error.response.status
  const data: unknown = error.response.data

  if (isAlphaInvestErrorEnvelope(data)) {
    return new ApiError({
      kind: 'http',
      status,
      code: data.error.code,
      message: data.error.message,
      details: data.error.details,
      requestId: data.meta.request_id,
      cause: error,
    })
  }

  if (isFastApiErrorPayload(data)) {
    return new ApiError({
      kind: 'http',
      status,
      message: getFastApiMessage(data.detail) ?? getHttpFallbackMessage(status),
      details: data.detail,
      cause: error,
    })
  }

  return new ApiError({
    kind: 'http',
    status,
    message: getHttpFallbackMessage(status),
    details: data,
    cause: error,
  })
}
