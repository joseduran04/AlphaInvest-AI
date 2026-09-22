export interface NavigationItem {
  label: string
  to: string
  end?: boolean
  requiredPermissions?: string[]
  anyRequiredPermissions?: string[]
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
    label: 'Inteligencia artificial',
    to: '/app/ai',
    requiredPermissions: ['analisis.leer', 'activos.leer'],
  },
  {
    label: 'Noticias',
    to: '/app/news',
    requiredPermissions: ['noticias.leer', 'activos.leer'],
  },
  {
    label: 'Notificaciones',
    to: '/app/notifications',
    requiredPermissions: ['notificaciones.leer'],
  },
  {
    label: 'Reportes',
    to: '/app/reports',
    requiredPermissions: ['reportes.leer'],
  },
  {
    label: 'Administración',
    to: '/app/admin',
    anyRequiredPermissions: ['reportes.administrar', 'notificaciones.administrar'],
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
