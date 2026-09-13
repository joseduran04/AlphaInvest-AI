import { useQuery } from '@tanstack/react-query'

import { assetRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useAsset(assetId: string | null, enabled = true) {
  return useQuery({
    queryKey: marketQueryKeys.asset(assetId ?? 'none'),
    queryFn: () => {
      if (!assetId) {
        throw new Error('Se requiere un activo para consultar su detalle')
      }

      return assetRequest(assetId)
    },
    enabled: enabled && assetId !== null,
  })
}
