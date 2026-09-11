import { NavLink } from 'react-router'

import { useAuth } from '@/features/auth/hooks/useAuth'

import { navigationItems } from './navigationItems'

interface AppSidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function AppSidebar({ isOpen, onClose }: AppSidebarProps) {
  const { hasPermission } = useAuth()

  const visibleItems = navigationItems.filter(
    (item) => item.requiredPermissions?.every((permission) => hasPermission(permission)) ?? true,
  )

  return (
    <>
      <button
        className={`app-sidebar-backdrop ${isOpen ? 'app-sidebar-backdrop--visible' : ''}`}
        type="button"
        aria-label="Cerrar navegación"
        onClick={onClose}
      />

      <aside className={`app-sidebar ${isOpen ? 'app-sidebar--open' : ''}`}>
        <div className="app-sidebar__brand">
          <span className="app-sidebar__brand-mark" aria-hidden="true">
            A
          </span>

          <div>
            <strong>AlphaInvest</strong>
            <span>AI</span>
          </div>
        </div>

        <nav className="app-sidebar__navigation" aria-label="Navegación principal">
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
