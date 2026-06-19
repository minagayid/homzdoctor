/** Central route path registry — reference these instead of hardcoding strings. */
export const PATHS = {
  // Public marketing site
  landing: '/',

  // Authenticated app (mounted under /app)
  dashboard: '/app',
  doctor: '/app/doctor',
  records: '/app/records',
  diagnosis: '/app/diagnosis',
  prescriptions: '/app/prescriptions',
  pharmacies: '/app/pharmacies',
  appointments: '/app/appointments',
  chat: '/app/chat',
  profile: '/app/profile',
  settings: '/app/settings',

  // Auth
  login: '/login',
  register: '/register',
} as const;

/** Default landing route for a given user role. */
export function roleHome(role?: string): string {
  return role === 'doctor' || role === 'admin' ? PATHS.doctor : PATHS.dashboard;
}
