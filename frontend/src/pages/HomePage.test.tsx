import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { AuthContextValue } from '@/features/auth/context/AuthContext'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { HomePage } from '@/pages/HomePage'

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}))

const mockedUseAuth = vi.mocked(useAuth)

const anonymous: AuthContextValue = {
  user: null,
  status: 'unauthenticated',
  error: null,
  isAuthenticated: false,
  login: vi.fn(),
  logout: vi.fn(),
  restore: vi.fn(),
  hasPermission: vi.fn(),
}

function renderHome() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/app" element={<div>Panel principal</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('HomePage', () => {
  beforeEach(() => {
    mockedUseAuth.mockReset()
  })

  it('ofrece iniciar sesión y crear cuenta a un visitante', () => {
    mockedUseAuth.mockReturnValue(anonymous)
    renderHome()

    expect(screen.getByRole('link', { name: 'Iniciar sesión' })).toHaveAttribute('href', '/login')
    expect(screen.getByRole('link', { name: 'Crear cuenta' })).toHaveAttribute('href', '/register')
  })

  it('manda al panel a quien ya tiene sesión', () => {
    mockedUseAuth.mockReturnValue({ ...anonymous, status: 'authenticated', isAuthenticated: true })
    renderHome()

    expect(screen.getByText('Panel principal')).toBeInTheDocument()
  })
})
