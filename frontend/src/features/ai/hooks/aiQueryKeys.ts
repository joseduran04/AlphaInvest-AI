export const aiQueryKeys = {
  all: ['ai'] as const,

  sentimentAnalysisRoot: () => [...aiQueryKeys.all, 'sentiment-analysis'] as const,

  sentimentAnalysisDetailRoot: (requestId: string) =>
    [...aiQueryKeys.sentimentAnalysisRoot(), 'detail', requestId] as const,

  sentimentAnalysisRequest: (requestId: string) =>
    [...aiQueryKeys.sentimentAnalysisDetailRoot(requestId), 'request'] as const,

  sentimentAnalysisResult: (requestId: string) =>
    [...aiQueryKeys.sentimentAnalysisDetailRoot(requestId), 'result'] as const,

  assetSentimentSummary: (assetId: string) =>
    [...aiQueryKeys.sentimentAnalysisRoot(), 'asset-summary', assetId] as const,
}
