import { useQuery } from '@tanstack/react-query'

import { riskProfileHistoryRequest } from '@/features/profile/api/profileApi'
import { profileQueryKeys } from '@/features/profile/hooks/profileQueryKeys'

export function useRiskProfileHistory() {
  return useQuery({
    queryKey: profileQueryKeys.history(),
    queryFn: riskProfileHistoryRequest,
  })
}
