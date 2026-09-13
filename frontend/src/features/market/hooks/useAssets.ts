import { useQuery } from '@tanstack/react-query'

import type { AssetListQuery } from '@/api/types'
import { assetsRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useAssets(params: AssetListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: marketQueryKeys.assets(params),
    queryFn: () => assetsRequest(params),
    enabled,
  })
}
