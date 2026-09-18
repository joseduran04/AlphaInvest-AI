import type { AssetNewsListQuery } from '@/api/types'

export const newsQueryKeys = {
  all: ['news'] as const,

  assetNewsRoot: () => [...newsQueryKeys.all, 'assets'] as const,

  assetNews: (assetId: string, params: AssetNewsListQuery) =>
    [...newsQueryKeys.assetNewsRoot(), assetId, params] as const,
}
