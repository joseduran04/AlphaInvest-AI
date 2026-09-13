import { apiClient, publicApiClient } from '@/api/client'
import { ApiError } from '@/api/errors'
import type {
  CreateRiskEvaluationRequest,
  CurrentRiskProfileResponse,
  QuestionnaireResponse,
  RiskEvaluationResponse,
  RiskProfileHistoryResponse,
} from '@/api/types'

const QUESTIONNAIRE_PATH = '/api/v1/profile/questionnaire'
const CURRENT_PROFILE_PATH = '/api/v1/profile/current'
const PROFILE_HISTORY_PATH = '/api/v1/profile/history'
const EVALUATIONS_PATH = '/api/v1/profile/evaluations'

export async function riskQuestionnaireRequest(): Promise<QuestionnaireResponse> {
  const response = await publicApiClient.get<QuestionnaireResponse>(QUESTIONNAIRE_PATH)

  return response.data
}

export async function currentRiskProfileRequest(): Promise<CurrentRiskProfileResponse | null> {
  try {
    const response = await apiClient.get<CurrentRiskProfileResponse>(CURRENT_PROFILE_PATH)

    return response.data
  } catch (error) {
    if (error instanceof ApiError && error.kind === 'http' && error.status === 404) {
      return null
    }

    throw error
  }
}

export async function riskProfileHistoryRequest(): Promise<RiskProfileHistoryResponse> {
  const response = await apiClient.get<RiskProfileHistoryResponse>(PROFILE_HISTORY_PATH)

  return response.data
}

export async function createRiskEvaluationRequest(
  data: CreateRiskEvaluationRequest,
): Promise<RiskEvaluationResponse> {
  const response = await apiClient.post<RiskEvaluationResponse>(EVALUATIONS_PATH, data)

  return response.data
}
