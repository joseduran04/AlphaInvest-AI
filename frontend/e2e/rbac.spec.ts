import { expect, test, type Page } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

interface RoleScenario {
  name: string
  emailVariable: string
  passwordVariable: string
  visibleNavigation: string[]
  hiddenNavigation: string[]
  allowedRoutes: string[]
  forbiddenRoutes: string[]
}

const commonNavigation = ['Inicio', 'Mercado', 'Perfil de riesgo']

const scenarios: RoleScenario[] = [
  {
    name: 'ADMINISTRADOR',
    emailVariable: 'E2E_ADMIN_EMAIL',
    passwordVariable: 'E2E_ADMIN_PASSWORD',
    visibleNavigation: [
      'Inicio',
      'Mercado',
      'Portafolios',
      'Simulaciones',
      'Inteligencia artificial',
      'Noticias',
      'Notificaciones',
      'Reportes',
      'Administración',
      'Sincronizaciones',
      'Perfil de riesgo',
    ],
    hiddenNavigation: [],
    allowedRoutes: [
      '/app/market',
      '/app/portfolios',
      '/app/simulations',
      '/app/ai',
      '/app/news',
      '/app/notifications',
      '/app/reports',
      '/app/admin',
      '/app/market/synchronizations',
    ],
    forbiddenRoutes: [],
  },
  {
    name: 'ANALISTA',
    emailVariable: 'E2E_ANALYST_EMAIL',
    passwordVariable: 'E2E_ANALYST_PASSWORD',
    visibleNavigation: [
      ...commonNavigation,
      'Portafolios',
      'Simulaciones',
      'Inteligencia artificial',
      'Noticias',
      'Reportes',
      'Sincronizaciones',
    ],
    hiddenNavigation: ['Notificaciones', 'Administración'],
    allowedRoutes: [
      '/app/market',
      '/app/portfolios',
      '/app/simulations',
      '/app/ai',
      '/app/news',
      '/app/reports',
      '/app/market/synchronizations',
    ],
    forbiddenRoutes: ['/app/notifications', '/app/admin'],
  },
  {
    name: 'AUDITOR',
    emailVariable: 'E2E_AUDITOR_EMAIL',
    passwordVariable: 'E2E_AUDITOR_PASSWORD',
    visibleNavigation: [...commonNavigation, 'Reportes', 'Administración', 'Sincronizaciones'],
    hiddenNavigation: [
      'Portafolios',
      'Simulaciones',
      'Inteligencia artificial',
      'Noticias',
      'Notificaciones',
    ],
    allowedRoutes: ['/app/market', '/app/reports', '/app/admin', '/app/market/synchronizations'],
    forbiddenRoutes: [
      '/app/portfolios',
      '/app/simulations',
      '/app/ai',
      '/app/news',
      '/app/notifications',
    ],
  },
  {
    name: 'INVERSIONISTA',
    emailVariable: 'E2E_INVESTOR_EMAIL',
    passwordVariable: 'E2E_INVESTOR_PASSWORD',
    visibleNavigation: [
      ...commonNavigation,
      'Portafolios',
      'Simulaciones',
      'Inteligencia artificial',
      'Noticias',
      'Notificaciones',
      'Reportes',
    ],
    hiddenNavigation: ['Administración', 'Sincronizaciones'],
    allowedRoutes: [
      '/app/market',
      '/app/portfolios',
      '/app/simulations',
      '/app/ai',
      '/app/news',
      '/app/notifications',
      '/app/reports',
    ],
    forbiddenRoutes: ['/app/admin', '/app/market/synchronizations'],
  },
  {
    name: 'OPERADOR',
    emailVariable: 'E2E_OPERATOR_EMAIL',
    passwordVariable: 'E2E_OPERATOR_PASSWORD',
    visibleNavigation: [
      ...commonNavigation,
      'Noticias',
      'Notificaciones',
      'Reportes',
      'Administración',
      'Sincronizaciones',
    ],
    hiddenNavigation: ['Portafolios', 'Simulaciones', 'Inteligencia artificial'],
    allowedRoutes: [
      '/app/market',
      '/app/news',
      '/app/notifications',
      '/app/reports',
      '/app/admin',
      '/app/market/synchronizations',
    ],
    forbiddenRoutes: ['/app/portfolios', '/app/simulations', '/app/ai'],
  },
]

async function navigateWithinApp(page: Page, route: string): Promise<void> {
  await page.evaluate((targetRoute) => {
    window.history.pushState({}, '', targetRoute)
    window.dispatchEvent(new PopStateEvent('popstate'))
  }, route)
}

async function expectAllowedRoute(page: Page, route: string): Promise<void> {
  await navigateWithinApp(page, route)

  await expect(page).toHaveURL(route)
  await expect(page.getByRole('heading', { name: 'Acceso no autorizado' })).not.toBeVisible()
}

async function expectForbiddenRoute(page: Page, route: string): Promise<void> {
  await navigateWithinApp(page, route)

  await expect(page).toHaveURL(/\/forbidden$/)
  await expect(page.getByRole('heading', { name: 'Acceso no autorizado' })).toBeVisible()
}

for (const scenario of scenarios) {
  test.describe(`RBAC ${scenario.name}`, () => {
    test.beforeEach(async ({ page }) => {
      const credentials = getE2ECredentials(scenario.emailVariable, scenario.passwordVariable)

      await loginThroughUI(page, credentials)
    })

    test('muestra únicamente la navegación permitida', async ({ page }) => {
      const navigation = page.getByRole('navigation', {
        name: 'Navegación principal',
      })

      for (const label of scenario.visibleNavigation) {
        await expect(navigation.getByRole('link', { name: label, exact: true })).toBeVisible()
      }

      for (const label of scenario.hiddenNavigation) {
        await expect(navigation.getByRole('link', { name: label, exact: true })).toHaveCount(0)
      }
    })

    test('permite acceder directamente a las rutas autorizadas', async ({ page }) => {
      for (const route of scenario.allowedRoutes) {
        await expectAllowedRoute(page, route)
      }
    })

    if (scenario.forbiddenRoutes.length > 0) {
      test('bloquea el acceso directo a las rutas no autorizadas', async ({ page }) => {
        for (const route of scenario.forbiddenRoutes) {
          await expectForbiddenRoute(page, route)
        }
      })
    }
  })
}
