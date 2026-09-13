import { useQuery } from '@tanstack/react-query'

import type { LatestPriceQuery } from '@/api/types'
import { latestPriceRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useLatestPrice(
  assetId: string | null,
  params: LatestPriceQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: marketQueryKeys.latestPrice(assetId ?? 'none', params),
    queryFn: () => {
      if (!assetId) {
        throw new Error('Se requiere un activo para consultar su último precio')
      }

      return latestPriceRequest(assetId, params)
    },
    enabled: enabled && assetId !== null,
  })
}
