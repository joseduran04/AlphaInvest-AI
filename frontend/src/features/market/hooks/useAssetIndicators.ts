import { useQuery } from '@tanstack/react-query'

import type { FinancialIndicatorListQuery } from '@/api/types'
import { assetIndicatorsRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function useAssetIndicators(
  assetId: string | null,
  params: FinancialIndicatorListQuery = {},
  enabled = true,
) {
  return useQuery({
    queryKey: marketQueryKeys.indicators(assetId ?? 'none', params),
    queryFn: () => {
      if (!assetId) {
        throw new Error('Se requiere un activo para consultar sus indicadores')
      }

      return assetIndicatorsRequest(assetId, params)
    },
    enabled: enabled && assetId !== null,
  })
}
