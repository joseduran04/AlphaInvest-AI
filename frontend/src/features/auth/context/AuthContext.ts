import { createContext } from 'react'

import type { LoginRequest, UserResponse } from '@/api/types'

export type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated' | 'error'

export interface AuthContextValue {
  user: UserResponse | null
  status: AuthStatus
  error: Error | null
  isAuthenticated: boolean
  login: (data: LoginRequest) => Promise<UserResponse>
  logout: () => Promise<void>
  restore: () => Promise<void>
  hasPermission: (permission: string) => boolean
}

export const AuthContext = createContext<AuthContextValue | null>(null)
