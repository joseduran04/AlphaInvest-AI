import { expect, test } from '@playwright/test'

import { getE2ECredentials, loginThroughUI } from './support/auth'

test.describe('Simulaciones', () => {
  test('permite crear una configuración histórica y consultar su detalle', async ({ page }) => {
    const credentials = getE2ECredentials('E2E_ADMIN_EMAIL', 'E2E_ADMIN_PASSWORD')
    const simulationName = `E2E Simulation ${Date.now()}`
    const simulationDescription = 'Simulación histórica creada por Playwright E2E'

    await loginThroughUI(page, credentials)

    const initialConfigurationsResponse = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/simulations/configurations' &&
        url.searchParams.get('limit') === '20' &&
        url.searchParams.get('offset') === '0'
      )
    })

    await page.getByRole('link', { name: 'Simulaciones', exact: true }).click()

    await expect(page).toHaveURL(/\/app\/simulations$/)
    await expect(page.getByRole('heading', { name: 'Simulaciones de inversión' })).toBeVisible()

    const configurationsResponse = await initialConfigurationsResponse
    expect(configurationsResponse.ok()).toBe(true)

    await page
      .locator('.simulation-page__header')
      .getByRole('button', { name: 'Nueva simulación', exact: true })
      .click()

    await expect(page.getByRole('heading', { name: 'Crear configuración histórica' })).toBeVisible()

    await page.getByLabel('Nombre').fill(simulationName)
    await page.getByLabel('Descripción').fill(simulationDescription)
    await page.getByLabel('Moneda base').fill('USD')
    await page.getByLabel('Capital inicial').fill('10000')
    await page.getByLabel('Fecha de inicio').fill('2026-04-01')
    await page.getByLabel('Fecha final').fill('2026-07-31')

    const createConfigurationResponse = page.waitForResponse((response) => {
      const url = new URL(response.url())

      return (
        response.request().method() === 'POST' &&
        url.pathname === '/api/v1/simulations/configurations'
      )
    })

    const refreshedConfigurationsResponse = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return (
        url.pathname === '/api/v1/simulations/configurations' &&
        url.searchParams.get('limit') === '20' &&
        url.searchParams.get('offset') === '0'
      )
    })

    await page
      .locator('.simulation-create')
      .getByRole('button', { name: 'Crear configuración', exact: true })
      .click()

    const createdResponse = await createConfigurationResponse
    expect(createdResponse.ok()).toBe(true)

    const refreshedResponse = await refreshedConfigurationsResponse
    expect(refreshedResponse.ok()).toBe(true)

    await expect(page.getByRole('heading', { name: 'Crear configuración histórica' })).toBeHidden()

    const createdSimulation = page.locator('.simulation-card').filter({
      has: page.locator('.simulation-card__header strong', {
        hasText: simulationName,
      }),
    })

    await expect(createdSimulation).toBeVisible()
    await expect(createdSimulation.getByText(simulationDescription, { exact: true })).toBeVisible()
    await expect(createdSimulation.getByText('Histórica', { exact: true })).toBeVisible()
    await expect(createdSimulation.getByText('Borrador', { exact: true })).toBeVisible()
    await expect(createdSimulation.getByText('USD', { exact: true })).toBeVisible()
    await expect(createdSimulation.getByText('2026-04-01', { exact: true })).toBeVisible()
    await expect(createdSimulation.getByText('2026-07-31', { exact: true })).toBeVisible()

    const detailResponse = page.waitForResponse((response) => {
      if (response.request().method() !== 'GET') {
        return false
      }

      const url = new URL(response.url())

      return /^\/api\/v1\/simulations\/configurations\/[^/]+$/.test(url.pathname)
    })

    await createdSimulation.getByRole('link', { name: 'Ver configuración' }).click()

    await expect(page).toHaveURL(/\/app\/simulations\/[^/]+$/)

    const configurationResponse = await detailResponse
    expect(configurationResponse.ok()).toBe(true)

    await expect(page.getByRole('heading', { name: simulationName, exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Datos de la configuración' })).toBeVisible()
    await expect(page.getByText(simulationDescription, { exact: true })).toBeVisible()

    const generalInformation = page.locator('.simulation-detail-section').filter({
      has: page.getByRole('heading', { name: 'Datos de la configuración' }),
    })

    await expect(generalInformation).toBeVisible()
    await expect(generalInformation.getByText('Histórica', { exact: true })).toBeVisible()
    await expect(generalInformation.getByText('USD', { exact: true })).toBeVisible()
    await expect(generalInformation.getByText('Borrador', { exact: true })).toBeVisible()

    await page.getByRole('link', { name: '← Volver a simulaciones' }).click()

    await expect(page).toHaveURL(/\/app\/simulations$/)
    await expect(page.getByRole('heading', { name: 'Simulaciones de inversión' })).toBeVisible()
  })
})
