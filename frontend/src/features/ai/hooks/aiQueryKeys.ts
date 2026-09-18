export const aiQueryKeys = {
  all: ['ai'] as const,

  assetAnalysisRoot: () => [...aiQueryKeys.all, 'asset-analysis'] as const,

  assetAnalysisDetailRoot: (requestId: string) =>
    [...aiQueryKeys.assetAnalysisRoot(), 'detail', requestId] as const,

  assetAnalysisRequest: (requestId: string) =>
    [...aiQueryKeys.assetAnalysisDetailRoot(requestId), 'request'] as const,

  assetAnalysisResult: (requestId: string) =>
    [...aiQueryKeys.assetAnalysisDetailRoot(requestId), 'result'] as const,

  sentimentAnalysisRoot: () => [...aiQueryKeys.all, 'sentiment-analysis'] as const,

  sentimentAnalysisDetailRoot: (requestId: string) =>
    [...aiQueryKeys.sentimentAnalysisRoot(), 'detail', requestId] as const,

  sentimentAnalysisRequest: (requestId: string) =>
    [...aiQueryKeys.sentimentAnalysisDetailRoot(requestId), 'request'] as const,

  sentimentAnalysisResult: (requestId: string) =>
    [...aiQueryKeys.sentimentAnalysisDetailRoot(requestId), 'result'] as const,

  recommendationRoot: () => [...aiQueryKeys.all, 'recommendations'] as const,

  recommendationDetailRoot: (requestId: string) =>
    [...aiQueryKeys.recommendationRoot(), 'detail', requestId] as const,

  recommendationRequest: (requestId: string) =>
    [...aiQueryKeys.recommendationDetailRoot(requestId), 'request'] as const,

  recommendationResult: (requestId: string) =>
    [...aiQueryKeys.recommendationDetailRoot(requestId), 'result'] as const,

  integralAnalysisRoot: () => [...aiQueryKeys.all, 'integral-analysis'] as const,

  integralAnalysisDetailRoot: (requestId: string) =>
    [...aiQueryKeys.integralAnalysisRoot(), 'detail', requestId] as const,

  integralAnalysisRequest: (requestId: string) =>
    [...aiQueryKeys.integralAnalysisDetailRoot(requestId), 'request'] as const,

  integralAnalysisResult: (requestId: string) =>
    [...aiQueryKeys.integralAnalysisDetailRoot(requestId), 'result'] as const,
}
