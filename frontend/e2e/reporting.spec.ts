import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Reportes', () => {
  test('permite filtrar el reporte de activos y solicitar su exportación CSV', async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')

    await loginThroughUI(page, credentials)

    await page.getByRole('link', { name: 'Reportes', exact: true }).click()

    await expect(page).toHaveURL(/\/app\/reports$/)
    await expect(page.getByRole('heading', { name: 'Centro de reportes' })).toBeVisible()

    const assetReportCard = page.locator('.reporting-card').filter({
      has: page.getByRole('heading', { name: 'Activos' }),
    })

    const initialReportResponsePromise = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/reports/assets' &&
        url.searchParams.get('limit') !== null &&
        url.searchParams.get('offset') === '0' &&
        !url.searchParams.has('symbol')
      )
    })

    await assetReportCard.getByRole('link', { name: 'Consultar reporte' }).click()

    await expect(page).toHaveURL(/\/app\/reports\/assets$/)
    await expect(
      page.getByRole('heading', { name: 'Reporte de activos', exact: true }),
    ).toBeVisible()

    const initialReportResponse = await initialReportResponsePromise
    expect(initialReportResponse.ok()).toBe(true)

    const table = page.getByRole('table')
    await expect(table).toBeVisible()

    const firstDataRow = table.locator('tbody tr').first()
    await expect(firstDataRow).toBeVisible()

    const symbol = (await firstDataRow.locator('td').first().locator('strong').innerText()).trim()

    expect(symbol.length).toBeGreaterThan(0)

    const filters = page.locator('.reporting-filters')

    await filters.getByLabel('Símbolo').fill(symbol)

    const filteredReportResponsePromise = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/reports/assets' &&
        url.searchParams.get('symbol') === symbol &&
        url.searchParams.get('offset') === '0'
      )
    })

    await filters.getByRole('button', { name: 'Aplicar filtros' }).click()

    const filteredReportResponse = await filteredReportResponsePromise
    expect(filteredReportResponse.ok()).toBe(true)

    await expect(table).toBeVisible()

    const filteredRows = table.locator('tbody tr')
    expect(await filteredRows.count()).toBeGreaterThan(0)

    await expect(filteredRows.first().locator('td').first().locator('strong')).toHaveText(symbol)

    const exportResponsePromise = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/reports/export/assets' &&
        url.searchParams.get('symbol') === symbol &&
        url.searchParams.get('limit') === '5000' &&
        url.searchParams.get('offset') === '0'
      )
    })

    await page.getByRole('button', { name: 'Exportar CSV' }).click()

    const exportResponse = await exportResponsePromise

    expect(exportResponse.ok()).toBe(true)

    const contentType = exportResponse.headers()['content-type'] ?? ''
    const contentDisposition = exportResponse.headers()['content-disposition'] ?? ''

    expect(contentType.toLowerCase()).toContain('text/csv')
    expect(contentDisposition.toLowerCase()).toContain('attachment')
    expect(contentDisposition.toLowerCase()).toContain('.csv')
  })
})
