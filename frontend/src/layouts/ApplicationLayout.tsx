import { useState } from 'react'
import { Outlet } from 'react-router'

import { AppHeader } from '@/components/navigation/AppHeader'
import { AppSidebar } from '@/components/navigation/AppSidebar'

export function ApplicationLayout() {
  const [isNavigationOpen, setIsNavigationOpen] = useState(false)

  return (
    <div className="application-shell">
      <AppSidebar isOpen={isNavigationOpen} onClose={() => setIsNavigationOpen(false)} />

      <div className="application-shell__body">
        <AppHeader onOpenNavigation={() => setIsNavigationOpen(true)} />

        <main className="application-shell__content">
          <div className="application-shell__content-inner">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
