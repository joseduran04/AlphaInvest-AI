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
})
