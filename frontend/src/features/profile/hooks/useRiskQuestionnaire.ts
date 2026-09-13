import { useQuery } from '@tanstack/react-query'

import { riskQuestionnaireRequest } from '@/features/profile/api/profileApi'
import { profileQueryKeys } from '@/features/profile/hooks/profileQueryKeys'

export function useRiskQuestionnaire() {
  return useQuery({
    queryKey: profileQueryKeys.questionnaire(),
    queryFn: riskQuestionnaireRequest,
  })
}
