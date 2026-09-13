import type { components } from '@/api/generated/openapi'

export type LoginRequest = components['schemas']['LoginRequest']
export type LogoutRequest = components['schemas']['LogoutRequest']
export type RefreshRequest = components['schemas']['RefreshRequest']
export type RegisterRequest = components['schemas']['RegisterRequest']
export type TokenResponse = components['schemas']['TokenResponse']
export type UserResponse = components['schemas']['UserResponse']

export type AnswerOptionResponse = components['schemas']['AnswerOptionResponse']
export type QuestionResponse = components['schemas']['QuestionResponse']
export type QuestionnaireResponse = components['schemas']['QuestionnaireResponse']
export type CreateRiskEvaluationRequest = components['schemas']['CreateRiskEvaluationRequest']
export type CurrentRiskProfileResponse = components['schemas']['CurrentRiskProfileResponse']
export type RiskEvaluationResponse = components['schemas']['RiskEvaluationResponse']
export type RiskProfileHistoryResponse = components['schemas']['RiskProfileHistoryResponse']
