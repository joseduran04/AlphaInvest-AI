import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Mercado', () => {
  test('permite buscar un activo existente y consultar su detalle', async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')

    await loginThroughUI(page, credentials)

    const initialAssetsResponse = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return url.pathname === '/api/v1/market/assets' && url.searchParams.get('limit') === '20'
    })

    await page.getByRole('link', { name: 'Mercado', exact: true }).click()

    await expect(page).toHaveURL(/\/app\/market$/)
    await expect(page.getByRole('heading', { name: 'Explorador de activos' })).toBeVisible()

    const assetsResponse = await initialAssetsResponse

    expect(assetsResponse.ok()).toBe(true)

    const firstAsset = page.locator('.market-asset').first()

    await expect(firstAsset).toBeVisible()

    const symbol = (await firstAsset.locator('.market-asset__header strong').textContent())?.trim()

    expect(symbol).toBeTruthy()

    const filteredAssetsResponse = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return url.pathname === '/api/v1/market/assets' && url.searchParams.get('search') === symbol
    })

    await page.getByRole('searchbox', { name: 'Buscar' }).fill(symbol!)

    await page.getByRole('button', { name: 'Aplicar filtros' }).click()

    const searchResponse = await filteredAssetsResponse

    expect(searchResponse.ok()).toBe(true)

    const filteredAsset = page.locator('.market-asset').filter({
      has: page.locator('.market-asset__header strong', {
        hasText: symbol!,
      }),
    })

    await expect(filteredAsset).toBeVisible()

    await filteredAsset.getByRole('link', { name: 'Ver detalle' }).click()

    await expect(page).toHaveURL(/\/app\/market\/assets\/[^/]+$/)

    await expect(
      page.getByRole('heading', {
        name: new RegExp(`^${escapeRegExp(symbol!)}\\s*·`),
      }),
    ).toBeVisible()

    await expect(page.getByText('Datos del activo', { exact: true })).toBeVisible()

    await page.getByRole('link', { name: '← Volver al mercado' }).click()

    await expect(page).toHaveURL(/\/app\/market$/)
    await expect(page.getByRole('heading', { name: 'Explorador de activos' })).toBeVisible()
  })
})

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
