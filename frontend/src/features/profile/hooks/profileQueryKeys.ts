export const profileQueryKeys = {
  all: ['profile'] as const,
  questionnaire: () => [...profileQueryKeys.all, 'questionnaire'] as const,
  current: () => [...profileQueryKeys.all, 'current'] as const,
  history: () => [...profileQueryKeys.all, 'history'] as const,
}
