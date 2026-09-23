import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Portafolios', () => {
  test('permite crear un portafolio y consultar su detalle', async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')
    const portfolioName = `E2E Portfolio ${Date.now()}`
    const portfolioDescription = 'Portafolio creado por Playwright E2E'

    await loginThroughUI(page, credentials)

    const initialPortfoliosResponse = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/portfolios' &&
        url.searchParams.get('limit') === '20' &&
        url.searchParams.get('offset') === '0'
      )
    })

    await page.getByRole('link', { name: 'Portafolios', exact: true }).click()

    await expect(page).toHaveURL(/\/app\/portfolios$/)
    await expect(page.getByRole('heading', { name: 'Mis portafolios' })).toBeVisible()

    const portfoliosResponse = await initialPortfoliosResponse
    expect(portfoliosResponse.ok()).toBe(true)

    await page
      .locator('.portfolio-page__header')
      .getByRole('button', { name: 'Crear portafolio', exact: true })
      .click()

    await expect(page.getByRole('heading', { name: 'Crear portafolio' })).toBeVisible()

    await page.getByLabel('Nombre').fill(portfolioName)
    await page.getByLabel('Descripción').fill(portfolioDescription)
    await page.getByLabel('Moneda base').fill('USD')
    await page.getByLabel('Capital inicial').fill('10000')
    await page.getByLabel('Tipo').selectOption('VIRTUAL')

    const createPortfolioResponse = page.waitForResponse((response) => {
      const url = new URL(response.url())

      return response.request().method() === 'POST' && url.pathname === '/api/v1/portfolios'
    })

    const refreshedPortfoliosResponse = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/portfolios' &&
        url.searchParams.get('limit') === '20' &&
        url.searchParams.get('offset') === '0'
      )
    })

    await page
      .locator('.portfolio-create')
      .getByRole('button', { name: 'Crear portafolio', exact: true })
      .click()

    const createdResponse = await createPortfolioResponse
    expect(createdResponse.ok()).toBe(true)

    const refreshedResponse = await refreshedPortfoliosResponse
    expect(refreshedResponse.ok()).toBe(true)

    await expect(page.getByRole('heading', { name: 'Crear portafolio' })).toBeHidden()

    const createdPortfolio = page.locator('.portfolio-card').filter({
      has: page.locator('.portfolio-card__header strong', {
        hasText: portfolioName,
      }),
    })

    await expect(createdPortfolio).toBeVisible()
    await expect(createdPortfolio.getByText(portfolioDescription, { exact: true })).toBeVisible()
    await expect(createdPortfolio.getByText('USD', { exact: true })).toBeVisible()
    await expect(createdPortfolio.getByText('Virtual', { exact: true })).toBeVisible()
    await expect(createdPortfolio.getByText('Activo', { exact: true })).toBeVisible()

    const detailResponse = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return /^\/api\/v1\/portfolios\/[^/]+$/.test(url.pathname)
    })

    await createdPortfolio.getByRole('link', { name: 'Ver detalle' }).click()

    await expect(page).toHaveURL(/\/app\/portfolios\/[^/]+$/)

    const portfolioResponse = await detailResponse
    expect(portfolioResponse.ok()).toBe(true)

    await expect(page.getByRole('heading', { name: portfolioName, exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Datos del portafolio' })).toBeVisible()
    await expect(page.getByText(portfolioDescription, { exact: true })).toBeVisible()

    const generalInformation = page.locator('.portfolio-detail-section').filter({
      has: page.getByRole('heading', { name: 'Datos del portafolio' }),
    })

    await expect(generalInformation).toBeVisible()
    await expect(generalInformation.getByText('USD', { exact: true })).toBeVisible()
    await expect(generalInformation.getByText('Virtual', { exact: true })).toBeVisible()

    await page.getByRole('link', { name: '← Volver a portafolios' }).click()

    await expect(page).toHaveURL(/\/app\/portfolios$/)
    await expect(page.getByRole('heading', { name: 'Mis portafolios' })).toBeVisible()
  })
})
