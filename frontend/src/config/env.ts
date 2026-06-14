/**
 * Centralized, typed access to environment variables.
 * Import from here instead of reading import.meta.env directly.
 */
export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  wsUrl: import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/ws',
  appName: import.meta.env.VITE_APP_NAME ?? 'HomzDoctor',
  appVersion: import.meta.env.VITE_APP_VERSION ?? '0.1.0',
  googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '',
} as const;

/** Server origin without the /api/v1 prefix (for endpoints like /health). */
export const apiOrigin = env.apiBaseUrl.replace(/\/api\/v1\/?$/, '');
