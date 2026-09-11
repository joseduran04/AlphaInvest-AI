export interface NavigationItem {
  label: string
  to: string
  end?: boolean
  requiredPermissions?: string[]
}

export const navigationItems: NavigationItem[] = [
  {
    label: 'Inicio',
    to: '/app',
    end: true,
  },
]
