import { useQuery } from '@tanstack/react-query'

import { priceSeriesRequest } from '@/features/market/api/marketApi'
import { marketQueryKeys } from '@/features/market/hooks/marketQueryKeys'

export function usePriceSeries(assetId: string | null, startDate: string | null) {
  return useQuery({
    queryKey: [...marketQueryKeys.all, 'price-series', assetId, startDate],
    queryFn: () => priceSeriesRequest(assetId ?? '', startDate),
    enabled: assetId !== null,
    placeholderData: (previous) => previous,
  })
}
