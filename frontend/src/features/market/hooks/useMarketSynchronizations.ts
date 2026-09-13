import { useQuery } from '@tanstack/react-query'

import type { MarketSynchronizationListQuery } from '@/api/types'
import { marketSynchronizationsRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useMarketSynchronizations(
  params: MarketSynchronizationListQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: marketQueryKeys.synchronizations(params),
    queryFn: () => marketSynchronizationsRequest(params),
    enabled,
  })
}
