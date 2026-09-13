import { useQuery } from '@tanstack/react-query'

import type { FinancialSourceListQuery } from '@/api/types'
import { financialSourcesRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useFinancialSources(params: FinancialSourceListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: marketQueryKeys.financialSources(params),
    queryFn: () => financialSourcesRequest(params),
    enabled,
  })
}
