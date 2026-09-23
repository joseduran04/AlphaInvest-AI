import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Inteligencia artificial', () => {
  test('permite solicitar una predicción para un activo disponible', async ({ page }) => {
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
    await expect(page.getByRole('heading', { name: 'Análisis inteligente' })).toBeVisible()

    const assetsResponse = await assetsResponsePromise
    expect(assetsResponse.ok()).toBe(true)

    const modeNavigation = page.getByRole('navigation', { name: 'Tipos de análisis' })

    await expect(modeNavigation.getByRole('button', { name: 'Predicción' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
    await expect(modeNavigation.getByRole('button', { name: 'Sentimiento' })).toBeVisible()
    await expect(modeNavigation.getByRole('button', { name: 'Recomendación' })).toBeVisible()
    await expect(modeNavigation.getByRole('button', { name: 'Integral' })).toBeVisible()

    const analysisForm = page.locator('.ai-analysis-form').filter({
      has: page.getByRole('heading', { name: 'Analizar activo' }),
    })

    await expect(analysisForm).toBeVisible()

    const assetSelect = analysisForm.getByLabel('Activo')
    const availableOptions = assetSelect.locator('option:not([value=""])')

    expect(await availableOptions.count()).toBeGreaterThan(0)

    const firstAssetValue = await availableOptions.first().getAttribute('value')

    expect(firstAssetValue).not.toBeNull()

    await assetSelect.selectOption(firstAssetValue!)
    await analysisForm.getByLabel('Horizonte').selectOption('CORTO_PLAZO')
    await analysisForm.getByLabel('Fecha de referencia').fill('2026-07-31')

    const createAnalysisResponsePromise = page.waitForResponse((response) => {
      const url = new URL(response.url())

      return (
        response.request().method() === 'POST' && url.pathname === '/api/v1/ai/analysis-requests'
      )
    })

    await analysisForm.getByRole('button', { name: 'Iniciar análisis' }).click()

    const createAnalysisResponse = await createAnalysisResponsePromise

    expect(createAnalysisResponse.status()).toBe(201)

    await expect(page.getByRole('button', { name: 'Nuevo análisis' })).toBeVisible()

    await expect
      .poll(
        async () => {
          const waiting = page.getByText('En espera', { exact: true })
          const progress = page.locator('.ai-request__processing progress')

          if (await waiting.isVisible().catch(() => false)) {
            return true
          }

          if (await progress.isVisible().catch(() => false)) {
            return true
          }

          return false
        },
        {
          timeout: 10_000,
        },
      )
      .toBe(true)
  })
})
