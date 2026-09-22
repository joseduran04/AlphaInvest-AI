import { useEffect, useRef, useState } from 'react'
import { Outlet } from 'react-router'

import { AppHeader } from '@/components/navigation/AppHeader'
import { AppSidebar } from '@/components/navigation/AppSidebar'

export function ApplicationLayout() {
  const [isNavigationOpen, setIsNavigationOpen] = useState(false)
  const navigationTriggerRef = useRef<HTMLButtonElement>(null)

  const closeNavigation = () => {
    setIsNavigationOpen(false)
    navigationTriggerRef.current?.focus()
  }

  useEffect(() => {
    if (!isNavigationOpen) {
      return
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeNavigation()
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isNavigationOpen])

  return (
    <div className="application-shell">
      <AppSidebar isOpen={isNavigationOpen} onClose={closeNavigation} />

      <div className="application-shell__body">
        <AppHeader
          navigationTriggerRef={navigationTriggerRef}
          isNavigationOpen={isNavigationOpen}
          onOpenNavigation={() => setIsNavigationOpen(true)}
        />

        <main className="application-shell__content">
          <div className="application-shell__content-inner">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
