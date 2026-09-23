import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Autenticación', () => {
  test('ADMINISTRADOR puede iniciar sesión mediante la interfaz real', async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')

    await loginThroughUI(page, credentials)

    await expect(page.getByRole('heading', { name: /Bienvenido, RBAC/i })).toBeVisible()

    const navigation = page.getByRole('navigation', {
      name: 'Navegación principal',
    })

    await expect(navigation.getByRole('link', { name: 'Inicio', exact: true })).toBeVisible()
    await expect(
      navigation.getByRole('link', { name: 'Administración', exact: true }),
    ).toBeVisible()
  })

  test('ADMINISTRADOR puede cerrar sesión y no volver a una ruta protegida', async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')

    await loginThroughUI(page, credentials)

    const logoutResponsePromise = page.waitForResponse((response) => {
      const url = new URL(response.url())

      return response.request().method() === 'POST' && url.pathname === '/api/v1/auth/logout'
    })

    await page.getByRole('button', { name: 'Cerrar sesión' }).click()

    const logoutResponse = await logoutResponsePromise
    expect(logoutResponse.ok()).toBe(true)

    await expect(page).toHaveURL(/\/login$/)
    await expect(page.getByRole('button', { name: 'Iniciar sesión' })).toBeVisible()

    await page.goto('/app')

    await expect(page).toHaveURL(/\/login$/)
    await expect(page.getByRole('button', { name: 'Iniciar sesión' })).toBeVisible()
  })
})
