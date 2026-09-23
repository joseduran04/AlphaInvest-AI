import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Noticias', () => {
  test('permite consultar noticias para un activo disponible', async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')

    await loginThroughUI(page, credentials)

    const assetsResponsePromise = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/market/assets' &&
        url.searchParams.get('status') === 'ACTIVO' &&
        url.searchParams.get('limit') === '100' &&
        url.searchParams.get('offset') === '0'
      )
    })

    await page.getByRole('link', { name: 'Noticias', exact: true }).click()

    await expect(page).toHaveURL(/\/app\/news$/)
    await expect(
      page.getByRole('heading', { name: 'Noticias financieras', exact: true }),
    ).toBeVisible()

    const assetsResponse = await assetsResponsePromise
    expect(assetsResponse.ok()).toBe(true)

    const filters = page.locator('.news-filters')
    const assetSelect = filters.getByLabel('Activo')
    const availableOptions = assetSelect.locator('option:not([value=""])')

    expect(await availableOptions.count()).toBeGreaterThan(0)

    const firstAsset = availableOptions.first()
    const assetId = await firstAsset.getAttribute('value')
    const assetLabel = (await firstAsset.innerText()).trim()

    expect(assetId).not.toBeNull()
    expect(assetLabel.length).toBeGreaterThan(0)

    await assetSelect.selectOption(assetId!)

    const newsResponsePromise = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === `/api/v1/news/assets/${assetId}` &&
        url.searchParams.get('limit') === '20' &&
        url.searchParams.get('offset') === '0'
      )
    })

    await filters.getByRole('button', { name: 'Consultar noticias' }).click()

    const newsResponse = await newsResponsePromise
    expect(newsResponse.ok()).toBe(true)

    await expect(
      page.locator('.news-applied-filters').getByText(assetLabel, { exact: true }),
    ).toBeVisible()
    await expect
      .poll(
        async () => {
          const newsCards = page.locator('.news-card')
          const emptyState = page.getByRole('heading', {
            name: 'No se encontraron noticias',
            exact: true,
          })

          if ((await newsCards.count()) > 0) {
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

    await expect(page.getByRole('heading', { name: 'Sincronización de noticias' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Sincronizar noticias' })).toBeVisible()
  })
})
