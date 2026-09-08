const apiBaseUrlValue = import.meta.env.VITE_API_BASE_URL

if (!apiBaseUrlValue) {
  throw new Error('VITE_API_BASE_URL is not configured')
}

let apiBaseUrl: string

try {
  const url = new URL(apiBaseUrlValue)

  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    throw new Error('Unsupported API protocol')
  }

  apiBaseUrl = url.toString().replace(/\/$/, '')
} catch {
  throw new Error('VITE_API_BASE_URL must be a valid HTTP or HTTPS URL')
}

export const env = Object.freeze({
  apiBaseUrl,
})
