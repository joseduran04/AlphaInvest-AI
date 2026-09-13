import type { components, paths } from '@/api/generated/openapi'

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

export type PortfolioListResponse = components['schemas']['PortfolioListResponse']
export type PortfolioOverviewResponse = components['schemas']['PortfolioOverviewResponse']
export type PortfolioStatus = components['schemas']['PortfolioStatus']

export type SimulationExecutionListResponse =
  components['schemas']['SimulationExecutionListResponse']
export type SimulationExecutionStatus = components['schemas']['SimulationExecutionStatus']

export type NotificationListResponse = components['schemas']['NotificationListResponse']
export type UnreadNotificationCountResponse =
  components['schemas']['UnreadNotificationCountResponse']
export type NotificationPriority = components['schemas']['NotificationPriority']

export type RecommendationReportListResponse =
  components['schemas']['RecommendationReportListResponse']

export type AssetListResponse = components['schemas']['AssetListResponse']
export type AssetResponse = components['schemas']['AssetResponse']
export type AssetStatus = components['schemas']['AssetStatus']

export type MarketListResponse = components['schemas']['MarketListResponse']
export type AssetTypeListResponse = components['schemas']['AssetTypeListResponse']
export type FinancialSourceListResponse = components['schemas']['FinancialSourceListResponse']

export type HistoricalPriceListResponse = components['schemas']['HistoricalPriceListResponse']
export type LatestPriceResponse = components['schemas']['LatestPriceResponse']
export type PriceSynchronizationResponse = components['schemas']['PriceSynchronizationResponse']

export type FinancialIndicatorListResponse = components['schemas']['FinancialIndicatorListResponse']
export type FinancialIndicatorType = components['schemas']['FinancialIndicatorType']
export type IndicatorCalculationRequest = components['schemas']['IndicatorCalculationRequest']
export type IndicatorCalculationResponse = components['schemas']['IndicatorCalculationResponse']
export type JobExecutionListResponse = components['schemas']['JobExecutionListResponse']
export type JobExecutionResponse = components['schemas']['JobExecutionResponse']
export type JobExecutionStatus = components['schemas']['JobExecutionStatus']

export type MarketListQuery = NonNullable<
  paths['/api/v1/market/markets']['get']['parameters']['query']
>

export type AssetTypeListQuery = NonNullable<
  paths['/api/v1/market/asset-types']['get']['parameters']['query']
>

export type FinancialSourceListQuery = NonNullable<
  paths['/api/v1/market/sources']['get']['parameters']['query']
>

export type AssetListQuery = NonNullable<
  paths['/api/v1/market/assets']['get']['parameters']['query']
>

export type HistoricalPriceListQuery = NonNullable<
  paths['/api/v1/market/assets/{asset_id}/prices']['get']['parameters']['query']
>

export type LatestPriceQuery = NonNullable<
  paths['/api/v1/market/assets/{asset_id}/latest-price']['get']['parameters']['query']
>

export type FinancialIndicatorListQuery = NonNullable<
  paths['/api/v1/market/assets/{asset_id}/indicators']['get']['parameters']['query']
>

export type MarketSynchronizationListQuery = NonNullable<
  paths['/api/v1/market/synchronizations']['get']['parameters']['query']
>
