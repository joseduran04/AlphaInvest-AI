import { existsSync } from 'node:fs'
import { resolve } from 'node:path'

import { defineConfig, devices } from '@playwright/test'

const localEnvPath = resolve(process.cwd(), '.env.e2e.local')

if (existsSync(localEnvPath)) {
  process.loadEnvFile(localEnvPath)
}

const baseURL = process.env.E2E_BASE_URL ?? 'http://127.0.0.1:5173'
const apiBaseURL = process.env.E2E_API_BASE_URL ?? 'http://127.0.0.1:8000'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,

  reporter: [['list'], ['html', { open: 'never' }]],

  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
  ],

  webServer: {
    command: `npm run dev -- --host 127.0.0.1 --port 5173`,
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      ...process.env,
      VITE_API_BASE_URL: apiBaseURL,
    },
  },
})
