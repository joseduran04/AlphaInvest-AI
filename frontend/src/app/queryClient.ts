import { QueryClient } from '@tanstack/react-query'

import { ApiError } from '@/api/errors'

const MAX_RETRY_COUNT = 2

function shouldRetryRequest(failureCount: number, error: Error): boolean {
  if (failureCount >= MAX_RETRY_COUNT) {
    return false
  }

  if (!(error instanceof ApiError)) {
    return false
  }

  if (error.kind === 'network' || error.kind === 'timeout') {
    return true
  }

  if (error.kind === 'http' && error.status !== undefined) {
    return error.status >= 500
  }

  return false
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      gcTime: 5 * 60_000,
      retry: shouldRetryRequest,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
})
