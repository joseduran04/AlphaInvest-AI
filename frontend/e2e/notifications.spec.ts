import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Notificaciones', () => {
  test('permite consultar y filtrar las notificaciones del usuario', async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')

    await loginThroughUI(page, credentials)

    const notificationsResponsePromise = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/notifications' &&
        url.searchParams.get('unread_only') === 'false' &&
        url.searchParams.get('limit') === '20' &&
        url.searchParams.get('offset') === '0'
      )
    })

    const unreadCountResponsePromise = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return url.pathname === '/api/v1/notifications/unread-count'
    })

    await page.getByRole('link', { name: 'Notificaciones', exact: true }).click()

    await expect(page).toHaveURL(/\/app\/notifications$/)
    await expect(
      page.getByRole('heading', { name: 'Centro de notificaciones', exact: true }),
    ).toBeVisible()

    const [notificationsResponse, unreadCountResponse] = await Promise.all([
      notificationsResponsePromise,
      unreadCountResponsePromise,
    ])

    expect(notificationsResponse.ok()).toBe(true)
    expect(unreadCountResponse.ok()).toBe(true)

    await expect(page.getByText('No leídas', { exact: true }).first()).toBeVisible()

    await expect
      .poll(
        async () => {
          const cards = page.locator('.notification-card')
          const emptyState = page.getByRole('heading', {
            name: 'No tienes notificaciones',
            exact: true,
          })

          if ((await cards.count()) > 0) {
            return 'results'
          }

          if (await emptyState.isVisible().catch(() => false)) {
            return 'empty'
          }

          return 'pending'
        },
        {
          timeout: 10_000,
        },
      )
      .not.toBe('pending')

    const unreadNotificationsResponsePromise = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/notifications' &&
        url.searchParams.get('unread_only') === 'true' &&
        url.searchParams.get('limit') === '20' &&
        url.searchParams.get('offset') === '0'
      )
    })

    await page
      .getByRole('group', { name: 'Filtrar notificaciones' })
      .getByRole('button', { name: 'No leídas', exact: true })
      .click()

    const unreadNotificationsResponse = await unreadNotificationsResponsePromise
    expect(unreadNotificationsResponse.ok()).toBe(true)

    await expect
      .poll(
        async () => {
          const cards = page.locator('.notification-card')
          const emptyState = page.getByRole('heading', {
            name: 'No tienes notificaciones sin leer',
            exact: true,
          })

          if ((await cards.count()) > 0) {
            return 'results'
          }

          if (await emptyState.isVisible().catch(() => false)) {
            return 'empty'
          }

          return 'pending'
        },
        {
          timeout: 10_000,
        },
      )
      .not.toBe('pending')
  })
})
