import { useQuery } from '@tanstack/react-query'

import type { MarketListQuery } from '@/api/types'
import { marketsRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useMarkets(params: MarketListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: marketQueryKeys.markets(params),
    queryFn: () => marketsRequest(params),
    enabled,
  })
}
