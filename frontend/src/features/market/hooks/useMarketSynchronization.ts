import { useQuery } from '@tanstack/react-query'

import { marketSynchronizationRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useMarketSynchronization(executionId: string, enabled = true) {
  return useQuery({
    queryKey: marketQueryKeys.synchronization(executionId),
    queryFn: () => marketSynchronizationRequest(executionId),
    enabled: enabled && executionId.length > 0,
  })
}
