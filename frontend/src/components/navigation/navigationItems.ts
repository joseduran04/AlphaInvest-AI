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
    label: 'Portafolios',
    to: '/app/portfolios',
    requiredPermissions: ['portafolios.leer'],
  },
  {
    label: 'Simulaciones',
    to: '/app/simulations',
    requiredPermissions: ['simulaciones.leer'],
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
