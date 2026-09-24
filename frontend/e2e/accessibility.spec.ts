import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

interface AccessibilityRoute {
  name: string
  route: string
  heading: string
  exactHeading?: boolean
}

const routes: AccessibilityRoute[] = [
  {
    name: 'dashboard',
    route: '/app',
    heading: 'Bienvenido',
    exactHeading: false,
  },
  {
    name: 'mercado',
    route: '/app/market',
    heading: 'Explorador de activos',
  },
  {
    name: 'portafolios',
    route: '/app/portfolios',
    heading: 'Mis portafolios',
  },
  {
    name: 'simulaciones',
    route: '/app/simulations',
    heading: 'Simulaciones de inversión',
  },
  {
    name: 'inteligencia artificial',
    route: '/app/ai',
    heading: 'Sentimiento de noticias',
  },
  {
    name: 'noticias',
    route: '/app/news',
    heading: 'Noticias financieras',
  },
  {
    name: 'notificaciones',
    route: '/app/notifications',
    heading: 'Centro de notificaciones',
  },
  {
    name: 'reportes',
    route: '/app/reports',
    heading: 'Centro de reportes',
  },
  {
    name: 'administración',
    route: '/app/admin',
    heading: 'Centro de administración',
  },
  {
    name: 'sincronizaciones',
    route: '/app/market/synchronizations',
    heading: 'Sincronizaciones',
  },
]

async function navigateWithinApp(page: Page, route: string): Promise<void> {
  await page.evaluate((targetRoute) => {
    window.history.pushState({}, '', targetRoute)
    window.dispatchEvent(new PopStateEvent('popstate'))
  }, route)
}

async function expectRouteReady(page: Page, route: AccessibilityRoute): Promise<void> {
  await navigateWithinApp(page, route.route)

  await expect(page).toHaveURL(route.route)
  await expect(
    page.getByRole('heading', {
      name: route.heading,
      exact: route.exactHeading ?? true,
    }),
  ).toBeVisible()
}

test.describe('Accesibilidad', () => {
  test.beforeEach(async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')

    await loginThroughUI(page, credentials)
  })

  for (const route of routes) {
    test(`${route.name} no presenta violaciones WCAG críticas o serias`, async ({ page }) => {
      await expectRouteReady(page, route)

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .analyze()

      const blockingViolations = accessibilityScanResults.violations.filter(
        (violation) => violation.impact === 'critical' || violation.impact === 'serious',
      )

      expect(blockingViolations).toEqual([])
    })
  }
})
