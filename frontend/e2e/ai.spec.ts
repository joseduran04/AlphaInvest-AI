import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Inteligencia artificial', () => {
  test('muestra el análisis de sentimiento y el termómetro de un activo', async ({ page }) => {
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

    await page.getByRole('link', { name: 'Inteligencia artificial', exact: true }).click()

    await expect(page).toHaveURL(/\/app\/ai$/)
    await expect(page.getByRole('heading', { name: 'Sentimiento de noticias' })).toBeVisible()

    const assetsResponse = await assetsResponsePromise
    expect(assetsResponse.ok()).toBe(true)

    // Los módulos retirados ya no se ofrecen.
    await expect(page.getByRole('navigation', { name: 'Tipos de análisis' })).toHaveCount(0)
    await expect(page.getByLabel('Horizonte')).toHaveCount(0)

    const sentimentForm = page.locator('.ai-analysis-form').filter({
      has: page.getByRole('heading', { name: 'Analizar sentimiento' }),
    })

    await expect(sentimentForm).toBeVisible()

    const assetSelect = sentimentForm.getByLabel('Activo')
    const availableOptions = assetSelect.locator('option:not([value=""])')

    expect(await availableOptions.count()).toBeGreaterThan(0)

    const firstAssetValue = await availableOptions.first().getAttribute('value')

    expect(firstAssetValue).not.toBeNull()

    const summaryResponsePromise = page.waitForResponse((response) => {
      const url = new URL(response.url())

      return (
        response.request().method() === 'GET' &&
        url.pathname === `/api/v1/ai/assets/${firstAssetValue}/sentiment-summary`
      )
    })

    await assetSelect.selectOption(firstAssetValue!)

    const summaryResponse = await summaryResponsePromise
    expect(summaryResponse.ok()).toBe(true)

    await expect(page.getByText('Termómetro de sentimiento', { exact: true })).toBeVisible()
  })
})
