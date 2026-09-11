import { apiClient, publicApiClient } from '@/api/client'
import type {
  LoginRequest,
  LogoutRequest,
  RegisterRequest,
  TokenResponse,
  UserResponse,
} from '@/api/types'

const REGISTER_PATH = '/api/v1/auth/register'
const LOGIN_PATH = '/api/v1/auth/login'
const LOGOUT_PATH = '/api/v1/auth/logout'
const ME_PATH = '/api/v1/auth/me'

export async function registerRequest(data: RegisterRequest): Promise<UserResponse> {
  const response = await publicApiClient.post<UserResponse>(REGISTER_PATH, data)

  return response.data
}

export async function loginRequest(data: LoginRequest): Promise<TokenResponse> {
  const response = await publicApiClient.post<TokenResponse>(LOGIN_PATH, data)

  return response.data
}

export async function logoutRequest(data: LogoutRequest): Promise<void> {
  await publicApiClient.post(LOGOUT_PATH, data)
}

export async function currentUserRequest(): Promise<UserResponse> {
  const response = await apiClient.get<UserResponse>(ME_PATH)

  return response.data
}
