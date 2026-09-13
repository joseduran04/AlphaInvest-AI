import { useQuery } from '@tanstack/react-query'

import { currentRiskProfileRequest } from '@/features/profile/api/profileApi'
import { profileQueryKeys } from '@/features/profile/hooks/profileQueryKeys'

export function useCurrentRiskProfile() {
  return useQuery({
    queryKey: profileQueryKeys.current(),
    queryFn: currentRiskProfileRequest,
  })
}
