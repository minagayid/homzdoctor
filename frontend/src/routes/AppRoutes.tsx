import { Routes, Route } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { PATHS } from './paths';
import LandingPage from '../pages/landing/LandingPage';
import { DashboardPage } from '../pages/DashboardPage';
import { RecordsPage } from '../pages/records/RecordsPage';
import { PrescriptionsPage } from '../pages/prescriptions/PrescriptionsPage';
import { PharmaciesPage } from '../pages/pharmacies/PharmaciesPage';
import { AppointmentsPage } from '../pages/appointments/AppointmentsPage';
import { ChatPage } from '../pages/chat/ChatPage';
import { SettingsPage } from '../pages/settings/SettingsPage';
import { LoginPage } from '../pages/auth/LoginPage';
import { RegisterPage } from '../pages/auth/RegisterPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export function AppRoutes() {
  return (
    <Routes>
      {/* Public marketing landing */}
      <Route path={PATHS.landing} element={<LandingPage />} />

      {/* Authenticated app shell (mounted under /app) */}
      <Route element={<Layout />}>
        <Route path={PATHS.dashboard} element={<DashboardPage />} />
        <Route path={PATHS.records} element={<RecordsPage />} />
        <Route path={PATHS.prescriptions} element={<PrescriptionsPage />} />
        <Route path={PATHS.pharmacies} element={<PharmaciesPage />} />
        <Route path={PATHS.appointments} element={<AppointmentsPage />} />
        <Route path={PATHS.chat} element={<ChatPage />} />
        <Route path={PATHS.settings} element={<SettingsPage />} />
      </Route>

      {/* Standalone (no shell) routes */}
      <Route path={PATHS.login} element={<LoginPage />} />
      <Route path={PATHS.register} element={<RegisterPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
