import type { SimulationConfigurationListQuery, SimulationExecutionListQuery } from '@/api/types'

export const simulationQueryKeys = {
  all: ['simulation'] as const,

  configurationListsRoot: () => [...simulationQueryKeys.all, 'configurations', 'list'] as const,

  configurations: (params: SimulationConfigurationListQuery = {}) =>
    [...simulationQueryKeys.configurationListsRoot(), params] as const,

  configurationDetailRoot: (configurationId: string) =>
    [...simulationQueryKeys.all, 'configurations', 'detail', configurationId] as const,

  configuration: (configurationId: string) =>
    [...simulationQueryKeys.configurationDetailRoot(configurationId), 'configuration'] as const,

  configurationAssetsRoot: (configurationId: string) =>
    [...simulationQueryKeys.configurationDetailRoot(configurationId), 'assets'] as const,

  configurationAssets: (configurationId: string) =>
    [...simulationQueryKeys.configurationAssetsRoot(configurationId), 'list'] as const,

  distribution: (configurationId: string) =>
    [...simulationQueryKeys.configurationDetailRoot(configurationId), 'distribution'] as const,

  configurationExecutionsRoot: (configurationId: string) =>
    [...simulationQueryKeys.configurationDetailRoot(configurationId), 'executions'] as const,

  executionListsRoot: () => [...simulationQueryKeys.all, 'executions', 'list'] as const,

  executions: (params: SimulationExecutionListQuery = {}) =>
    [...simulationQueryKeys.executionListsRoot(), params] as const,

  executionDetailRoot: (executionId: string) =>
    [...simulationQueryKeys.all, 'executions', 'detail', executionId] as const,

  execution: (executionId: string) =>
    [...simulationQueryKeys.executionDetailRoot(executionId), 'execution'] as const,

  result: (executionId: string) =>
    [...simulationQueryKeys.executionDetailRoot(executionId), 'result'] as const,
}
