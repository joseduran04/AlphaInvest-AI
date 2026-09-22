import { expect, type Page } from '@playwright/test'

export interface E2ECredentials {
  email: string
  password: string
}

export function getE2ECredentials(emailVariable: string, passwordVariable: string): E2ECredentials {
  const email = process.env[emailVariable]
  const password = process.env[passwordVariable]

  if (!email) {
    throw new Error(`${emailVariable} is not configured`)
  }

  if (!password) {
    throw new Error(`${passwordVariable} is not configured`)
  }

  return {
    email,
    password,
  }
}

export async function loginThroughUI(page: Page, credentials: E2ECredentials): Promise<void> {
  await page.goto('/login')

  await page.getByLabel('Correo electrónico').fill(credentials.email)
  await page.getByLabel('Contraseña').fill(credentials.password)

  await page.getByRole('button', { name: 'Iniciar sesión' }).click()

  await expect(page).toHaveURL(/\/app$/, { timeout: 15_000 })
  await expect(page.getByRole('navigation', { name: 'Navegación principal' })).toBeVisible()
}
