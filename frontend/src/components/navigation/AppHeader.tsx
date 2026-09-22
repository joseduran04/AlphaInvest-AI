import type { RefObject } from 'react'

import { useAuth } from '@/features/auth/hooks/useAuth'

interface AppHeaderProps {
  navigationTriggerRef: RefObject<HTMLButtonElement | null>
  isNavigationOpen: boolean
  onOpenNavigation: () => void
}

export function AppHeader({
  navigationTriggerRef,
  isNavigationOpen,
  onOpenNavigation,
}: AppHeaderProps) {
  const { user, logout } = useAuth()

  const displayName = [user?.nombres, user?.apellidos].filter(Boolean).join(' ')

  return (
    <header className="app-header">
      <div className="app-header__left">
        <button
          ref={navigationTriggerRef}
          className="app-header__menu"
          type="button"
          aria-label="Abrir navegación"
          aria-controls="app-sidebar"
          aria-expanded={isNavigationOpen}
          onClick={onOpenNavigation}
        >
          ☰
        </button>

        <div className="app-header__context">
          <span className="app-header__eyebrow">AlphaInvest AI</span>
          <strong>Panel de inversión</strong>
        </div>
      </div>

      <div className="app-header__user">
        <div className="app-header__identity">
          <strong>{displayName}</strong>
          <span>{user?.correo}</span>
        </div>

        <button className="app-header__logout" type="button" onClick={() => void logout()}>
          Cerrar sesión
        </button>
      </div>
    </header>
  )
}
