import { useQuery } from '@tanstack/react-query'

import type { AssetTypeListQuery } from '@/api/types'
import { assetTypesRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useAssetTypes(params: AssetTypeListQuery = {}, enabled = true) {
  return useQuery({
    queryKey: marketQueryKeys.assetTypes(params),
    queryFn: () => assetTypesRequest(params),
    enabled,
  })
}
