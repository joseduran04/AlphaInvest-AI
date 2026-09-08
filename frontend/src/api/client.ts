import axios, { AxiosHeaders, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

import { normalizeApiError } from '@/api/errors'
import { refreshSession } from '@/features/auth/session/sessionRefresh'
import { getAccessToken } from '@/features/auth/session/sessionStore'
import { env } from '@/lib/env'

interface RetriableRequestConfig extends InternalAxiosRequestConfig {
  authRetry?: boolean
}

function createBaseClient(): AxiosInstance {
  return axios.create({
    baseURL: env.apiBaseUrl,
    timeout: 15_000,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
  })
}

function installErrorNormalizer(client: AxiosInstance): void {
  client.interceptors.response.use(
    (response) => response,
    (error: unknown) => Promise.reject(normalizeApiError(error)),
  )
}

export const publicApiClient = createBaseClient()
export const apiClient = createBaseClient()

installErrorNormalizer(publicApiClient)

function requestHasBearerToken(config: InternalAxiosRequestConfig): boolean {
  const headers = AxiosHeaders.from(config.headers)
  const authorization = headers.get('Authorization')

  return typeof authorization === 'string' && authorization.startsWith('Bearer ')
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()

  if (!token) {
    return config
  }

  const headers = AxiosHeaders.from(config.headers)

  headers.set('Authorization', `Bearer ${token}`)

  config.headers = headers

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!axios.isAxiosError(error)) {
      return Promise.reject(normalizeApiError(error))
    }

    const status = error.response?.status
    const config = error.config as RetriableRequestConfig | undefined

    if (status !== 401 || !config || config.authRetry || !requestHasBearerToken(config)) {
      return Promise.reject(normalizeApiError(error))
    }

    config.authRetry = true

    try {
      await refreshSession()

      const token = getAccessToken()
      const headers = AxiosHeaders.from(config.headers)

      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      } else {
        headers.delete('Authorization')
      }

      config.headers = headers

      return apiClient.request(config)
    } catch (refreshError) {
      return Promise.reject(normalizeApiError(refreshError))
    }
  },
)
