/** Central route path registry — reference these instead of hardcoding strings. */
export const PATHS = {
  // Public marketing site
  landing: '/',

  // Authenticated app (mounted under /app)
  dashboard: '/app',
  records: '/app/records',
  prescriptions: '/app/prescriptions',
  pharmacies: '/app/pharmacies',
  appointments: '/app/appointments',
  chat: '/app/chat',
  settings: '/app/settings',

  // Auth
  login: '/login',
  register: '/register',
} as const;
