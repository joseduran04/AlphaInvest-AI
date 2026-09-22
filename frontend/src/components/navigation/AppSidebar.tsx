import { useEffect, useRef, useState } from 'react'
import { NavLink } from 'react-router'

import { useAuth } from '@/features/auth/hooks/useAuth'

import { navigationItems } from './navigationItems'

interface AppSidebarProps {
  isOpen: boolean
  onClose: () => void
}

const MOBILE_NAVIGATION_QUERY = '(max-width: 900px)'

export function AppSidebar({ isOpen, onClose }: AppSidebarProps) {
  const { hasPermission } = useAuth()
  const navigationRef = useRef<HTMLElement>(null)
  const [isMobileNavigation, setIsMobileNavigation] = useState(
    () => window.matchMedia(MOBILE_NAVIGATION_QUERY).matches,
  )

  useEffect(() => {
    const mediaQuery = window.matchMedia(MOBILE_NAVIGATION_QUERY)

    const handleChange = (event: MediaQueryListEvent) => {
      setIsMobileNavigation(event.matches)
    }

    mediaQuery.addEventListener('change', handleChange)

    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }, [])

  useEffect(() => {
    if (!isMobileNavigation || !isOpen) {
      return
    }

    const firstNavigationLink = navigationRef.current?.querySelector<HTMLAnchorElement>('a[href]')
    firstNavigationLink?.focus()
  }, [isMobileNavigation, isOpen])

  const visibleItems = navigationItems.filter((item) => {
    const hasAllRequiredPermissions =
      item.requiredPermissions?.every((permission) => hasPermission(permission)) ?? true

    const hasAnyRequiredPermission =
      !item.anyRequiredPermissions ||
      item.anyRequiredPermissions.some((permission) => hasPermission(permission))

    return hasAllRequiredPermissions && hasAnyRequiredPermission
  })

  const isMobileNavigationClosed = isMobileNavigation && !isOpen

  return (
    <>
      <button
        className={`app-sidebar-backdrop ${isOpen ? 'app-sidebar-backdrop--visible' : ''}`}
        type="button"
        aria-label="Cerrar navegación"
        aria-hidden={!isOpen}
        tabIndex={isOpen ? 0 : -1}
        onClick={onClose}
      />

      <aside
        id="app-sidebar"
        className={`app-sidebar ${isOpen ? 'app-sidebar--open' : ''}`}
        aria-label="Navegación de la aplicación"
        inert={isMobileNavigationClosed}
      >
        <div className="app-sidebar__brand">
          <span className="app-sidebar__brand-mark" aria-hidden="true">
            A
          </span>

          <div>
            <strong>AlphaInvest</strong>
            <span>AI</span>
          </div>
        </div>

        <nav
          ref={navigationRef}
          className="app-sidebar__navigation"
          aria-label="Navegación principal"
        >
          {visibleItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={onClose}
              className={({ isActive }) =>
                isActive ? 'app-sidebar__link app-sidebar__link--active' : 'app-sidebar__link'
              }
            >
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="app-sidebar__footer">
          <p>AlphaInvest AI</p>
          <span>Plataforma educativa de inversión</span>
        </div>
      </aside>
    </>
  )
}
