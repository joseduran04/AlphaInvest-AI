import { apiClient } from '@/api/client'
import type {
  SimulationConfigurationArchiveResponse,
  SimulationConfigurationAssetCreateRequest,
  SimulationConfigurationAssetListResponse,
  SimulationConfigurationAssetResponse,
  SimulationConfigurationAssetUpdateRequest,
  SimulationConfigurationCreateRequest,
  SimulationConfigurationListQuery,
  SimulationConfigurationListResponse,
  SimulationConfigurationReadyResponse,
  SimulationConfigurationResponse,
  SimulationConfigurationUpdateRequest,
  SimulationDistributionStatusResponse,
  SimulationExecutionCancelResponse,
  SimulationExecutionCreateRequest,
  SimulationExecutionListQuery,
  SimulationExecutionListResponse,
  SimulationExecutionResponse,
  SimulationResultResponse,
} from '@/api/types'

const SIMULATIONS_PATH = '/api/v1/simulations'

export async function simulationConfigurationsRequest(
  params: SimulationConfigurationListQuery = {},
): Promise<SimulationConfigurationListResponse> {
  const response = await apiClient.get<SimulationConfigurationListResponse>(
    `${SIMULATIONS_PATH}/configurations`,
    {
      params,
    },
  )

  return response.data
}

export async function simulationConfigurationRequest(
  configurationId: string,
): Promise<SimulationConfigurationResponse> {
  const response = await apiClient.get<SimulationConfigurationResponse>(
    `${SIMULATIONS_PATH}/configurations/${configurationId}`,
  )

  return response.data
}

export async function createSimulationConfigurationRequest(
  data: SimulationConfigurationCreateRequest,
): Promise<SimulationConfigurationResponse> {
  const response = await apiClient.post<SimulationConfigurationResponse>(
    `${SIMULATIONS_PATH}/configurations`,
    data,
  )

  return response.data
}

export async function updateSimulationConfigurationRequest(
  configurationId: string,
  data: SimulationConfigurationUpdateRequest,
): Promise<SimulationConfigurationResponse> {
  const response = await apiClient.patch<SimulationConfigurationResponse>(
    `${SIMULATIONS_PATH}/configurations/${configurationId}`,
    data,
  )

  return response.data
}

export async function archiveSimulationConfigurationRequest(
  configurationId: string,
): Promise<SimulationConfigurationArchiveResponse> {
  const response = await apiClient.post<SimulationConfigurationArchiveResponse>(
    `${SIMULATIONS_PATH}/configurations/${configurationId}/archive`,
  )

  return response.data
}

export async function simulationConfigurationAssetsRequest(
  configurationId: string,
): Promise<SimulationConfigurationAssetListResponse> {
  const response = await apiClient.get<SimulationConfigurationAssetListResponse>(
    `${SIMULATIONS_PATH}/configurations/${configurationId}/assets`,
  )

  return response.data
}

export async function addSimulationConfigurationAssetRequest(
  configurationId: string,
  data: SimulationConfigurationAssetCreateRequest,
): Promise<SimulationConfigurationAssetResponse> {
  const response = await apiClient.post<SimulationConfigurationAssetResponse>(
    `${SIMULATIONS_PATH}/configurations/${configurationId}/assets`,
    data,
  )

  return response.data
}

export async function updateSimulationConfigurationAssetRequest(
  configurationId: string,
  assetId: string,
  data: SimulationConfigurationAssetUpdateRequest,
): Promise<SimulationConfigurationAssetResponse> {
  const response = await apiClient.patch<SimulationConfigurationAssetResponse>(
    `${SIMULATIONS_PATH}/configurations/${configurationId}/assets/${assetId}`,
    data,
  )

  return response.data
}

export async function deleteSimulationConfigurationAssetRequest(
  configurationId: string,
  assetId: string,
): Promise<void> {
  await apiClient.delete(`${SIMULATIONS_PATH}/configurations/${configurationId}/assets/${assetId}`)
}

export async function simulationDistributionRequest(
  configurationId: string,
): Promise<SimulationDistributionStatusResponse> {
  const response = await apiClient.get<SimulationDistributionStatusResponse>(
    `${SIMULATIONS_PATH}/configurations/${configurationId}/distribution`,
  )

  return response.data
}

export async function markSimulationConfigurationReadyRequest(
  configurationId: string,
): Promise<SimulationConfigurationReadyResponse> {
  const response = await apiClient.post<SimulationConfigurationReadyResponse>(
    `${SIMULATIONS_PATH}/configurations/${configurationId}/ready`,
  )

  return response.data
}

export async function simulationExecutionsRequest(
  params: SimulationExecutionListQuery = {},
): Promise<SimulationExecutionListResponse> {
  const response = await apiClient.get<SimulationExecutionListResponse>(
    `${SIMULATIONS_PATH}/executions`,
    {
      params,
    },
  )

  return response.data
}

export async function simulationExecutionRequest(
  executionId: string,
): Promise<SimulationExecutionResponse> {
  const response = await apiClient.get<SimulationExecutionResponse>(
    `${SIMULATIONS_PATH}/executions/${executionId}`,
  )

  return response.data
}

export async function createSimulationExecutionRequest(
  data: SimulationExecutionCreateRequest,
): Promise<SimulationExecutionResponse> {
  const response = await apiClient.post<SimulationExecutionResponse>(
    `${SIMULATIONS_PATH}/executions`,
    data,
  )

  return response.data
}

export async function simulationExecutionResultRequest(
  executionId: string,
): Promise<SimulationResultResponse> {
  const response = await apiClient.get<SimulationResultResponse>(
    `${SIMULATIONS_PATH}/executions/${executionId}/result`,
  )

  return response.data
}

export async function cancelSimulationExecutionRequest(
  executionId: string,
): Promise<SimulationExecutionCancelResponse> {
  const response = await apiClient.post<SimulationExecutionCancelResponse>(
    `${SIMULATIONS_PATH}/executions/${executionId}/cancel`,
  )

  return response.data
}
