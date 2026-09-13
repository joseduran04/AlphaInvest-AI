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
  {
    label: 'Mercado',
    to: '/app/market',
    requiredPermissions: ['activos.leer'],
  },
  {
    label: 'Sincronizaciones',
    to: '/app/market/synchronizations',
    requiredPermissions: ['trabajos.leer'],
  },
  {
    label: 'Perfil de riesgo',
    to: '/app/profile',
  },
]
