import { useQuery } from '@tanstack/react-query'

import type { HistoricalPriceListQuery } from '@/api/types'
import { historicalPricesRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function usePriceHistory(
  assetId: string | null,
  params: HistoricalPriceListQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: marketQueryKeys.historicalPrices(assetId ?? 'none', params),
    queryFn: () => {
      if (!assetId) {
        throw new Error('Se requiere un activo para consultar su histórico de precios')
      }

      return historicalPricesRequest(assetId, params)
    },
    enabled: enabled && assetId !== null,
  })
}
