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

export type PortfolioCreateRequest = components['schemas']['PortfolioCreateRequest']
export type PortfolioUpdateRequest = components['schemas']['PortfolioUpdateRequest']
export type PortfolioResponse = components['schemas']['PortfolioResponse']
export type PortfolioListResponse = components['schemas']['PortfolioListResponse']
export type PortfolioOverviewResponse = components['schemas']['PortfolioOverviewResponse']
export type PortfolioCloseResponse = components['schemas']['PortfolioCloseResponse']
export type PortfolioStatus = components['schemas']['PortfolioStatus']
export type PortfolioType = components['schemas']['PortfolioType']

export type PositionCreateRequest = components['schemas']['PositionCreateRequest']
export type PositionUpdateRequest = components['schemas']['PositionUpdateRequest']
export type PositionResponse = components['schemas']['PositionResponse']
export type PositionListResponse = components['schemas']['PositionListResponse']
export type PositionStatus = components['schemas']['PositionStatus']

export type AssetAllocationResponse = components['schemas']['AssetAllocationResponse']
export type SectorAllocationResponse = components['schemas']['SectorAllocationResponse']

export type PortfolioValuationCreateRequest =
  components['schemas']['PortfolioValuationCreateRequest']
export type PortfolioValuationResponse = components['schemas']['PortfolioValuationResponse']
export type PortfolioValuationListResponse = components['schemas']['PortfolioValuationListResponse']

export type ContributionFrequency = components['schemas']['ContributionFrequency']
export type SimulationType = components['schemas']['SimulationType']
export type SimulationConfigurationStatus = components['schemas']['SimulationConfigurationStatus']

export type SimulationConfigurationCreateRequest =
  components['schemas']['SimulationConfigurationCreateRequest']
export type SimulationConfigurationUpdateRequest =
  components['schemas']['SimulationConfigurationUpdateRequest']
export type SimulationConfigurationResponse =
  components['schemas']['SimulationConfigurationResponse']
export type SimulationConfigurationListResponse =
  components['schemas']['SimulationConfigurationListResponse']
export type SimulationConfigurationArchiveResponse =
  components['schemas']['SimulationConfigurationArchiveResponse']

export type SimulationConfigurationAssetCreateRequest =
  components['schemas']['SimulationConfigurationAssetCreateRequest']
export type SimulationConfigurationAssetUpdateRequest =
  components['schemas']['SimulationConfigurationAssetUpdateRequest']
export type SimulationConfigurationAssetResponse =
  components['schemas']['SimulationConfigurationAssetResponse']
export type SimulationConfigurationAssetListResponse =
  components['schemas']['SimulationConfigurationAssetListResponse']

export type SimulationDistributionStatusResponse =
  components['schemas']['SimulationDistributionStatusResponse']
export type SimulationConfigurationReadyResponse =
  components['schemas']['SimulationConfigurationReadyResponse']

export type SimulationExecutionCreateRequest =
  components['schemas']['SimulationExecutionCreateRequest']
export type SimulationExecutionResponse = components['schemas']['SimulationExecutionResponse']
export type SimulationExecutionListResponse =
  components['schemas']['SimulationExecutionListResponse']
export type SimulationExecutionCancelResponse =
  components['schemas']['SimulationExecutionCancelResponse']
export type SimulationExecutionStatus = components['schemas']['SimulationExecutionStatus']

export type SimulationResultResponse = components['schemas']['SimulationResultResponse']
export type SimulationAssetResultResponse = components['schemas']['SimulationAssetResultResponse']

export type NotificationResponse = components['schemas']['NotificationResponse']
export type NotificationListResponse = components['schemas']['NotificationListResponse']
export type UnreadNotificationCountResponse =
  components['schemas']['UnreadNotificationCountResponse']
export type NotificationPriority = components['schemas']['NotificationPriority']

export type NotificationListQuery = NonNullable<
  paths['/api/v1/notifications']['get']['parameters']['query']
>

export type RecommendationReportListResponse =
  components['schemas']['RecommendationReportListResponse']
export type AnalysisHorizon = components['schemas']['AnalysisHorizon']
export type AnalysisType = components['schemas']['AnalysisType']
export type AnalysisRequestStatus = components['schemas']['AnalysisRequestStatus']

export type AssetAnalysisRequestCreate = components['schemas']['AssetAnalysisRequestCreate']
export type AnalysisRequestResponse = components['schemas']['AnalysisRequestResponse']
export type AssetAnalysisResultResponse = components['schemas']['AssetAnalysisResultResponse']
export type AssetPredictionProbabilitiesResponse =
  components['schemas']['AssetPredictionProbabilitiesResponse']

export type SentimentAnalysisRequestCreate = components['schemas']['SentimentAnalysisRequestCreate']
export type SentimentAnalysisResultResponse =
  components['schemas']['SentimentAnalysisResultResponse']

export type NewsResponse = components['schemas']['NewsResponse']
export type NewsListResponse = components['schemas']['NewsListResponse']
export type NewsSynchronizationResponse = components['schemas']['NewsSynchronizationResponse']

export type AssetNewsListQuery = NonNullable<
  paths['/api/v1/news/assets/{asset_id}']['get']['parameters']['query']
>

export type AssetNewsSynchronizationQuery = NonNullable<
  paths['/api/v1/news/assets/{asset_id}/sync']['post']['parameters']['query']
>

export type RecommendationRequestCreate = components['schemas']['RecommendationRequestCreate']
export type RecommendationResultResponse = components['schemas']['RecommendationResultResponse']
export type RecommendationAssetResponse = components['schemas']['RecommendationAssetResponse']
export type RecommendationEvidenceResponse = components['schemas']['RecommendationEvidenceResponse']

export type IntegralAnalysisRequestCreate = components['schemas']['IntegralAnalysisRequestCreate']
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

export type PortfolioListQuery = NonNullable<
  paths['/api/v1/portfolios']['get']['parameters']['query']
>

export type PortfolioPositionListQuery = NonNullable<
  paths['/api/v1/portfolios/{portfolio_id}/positions']['get']['parameters']['query']
>

export type PortfolioValuationListQuery = NonNullable<
  paths['/api/v1/portfolios/{portfolio_id}/valuations']['get']['parameters']['query']
>

export type SimulationConfigurationListQuery = NonNullable<
  paths['/api/v1/simulations/configurations']['get']['parameters']['query']
>

export type SimulationExecutionListQuery = NonNullable<
  paths['/api/v1/simulations/executions']['get']['parameters']['query']
>

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
