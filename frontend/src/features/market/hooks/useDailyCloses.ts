import { useQueries } from '@tanstack/react-query'

import { fetchDailyCloses } from '@/features/market/api/dailyCloses'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

/** Cierres diarios de varios activos desde una fecha (una consulta por activo). */
export function useDailyCloses(assetIds: string[], startDate: string | null, endDate?: string) {
  const queries = useQueries({
    queries: assetIds.map((assetId) => ({
      queryKey: [...marketQueryKeys.all, 'daily-closes', assetId, startDate, endDate ?? null],
      queryFn: () => fetchDailyCloses(assetId, startDate ?? '', endDate),
      enabled: startDate !== null,
      staleTime: 5 * 60 * 1000,
    })),
  })

  const closesByAsset = new Map<string, Map<string, number>>()

  queries.forEach((query, index) => {
    if (query.data) {
      closesByAsset.set(assetIds[index], query.data)
    }
  })

  return {
    closesByAsset,
    isPending: queries.some((query) => query.isPending),
    isError: queries.some((query) => query.isError),
    errorMessage: queries.find((query) => query.error)?.error?.message ?? null,
  }
}
