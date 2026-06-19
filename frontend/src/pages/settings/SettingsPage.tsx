import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Bell,
  SlidersHorizontal,
  Lock,
  ShieldCheck,
  Save,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { profileApi } from '../../api';
import type { Profile, ProfileUpdate } from '../../types';
import { Button, Card, PasswordInput, Spinner } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'ur', label: 'Urdu' },
  { value: 'ar', label: 'Arabic' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
];

const TIMEZONES = ['UTC', 'America/New_York', 'America/Los_Angeles', 'Europe/London', 'Asia/Karachi', 'Asia/Dubai'];
const THEMES = [
  { value: 'system', label: 'System' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
];

function Toggle({
  checked,
  onChange,
  label,
  hint,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
  hint?: string;
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-2">
      <div>
        <p className="text-sm font-medium text-slate-800">{label}</p>
        {hint && <p className="text-xs text-slate-500">{hint}</p>}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative h-6 w-11 shrink-0 rounded-full transition ${
          checked ? 'bg-teal-600' : 'bg-slate-300'
        }`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition ${
            checked ? 'left-[22px]' : 'left-0.5'
          }`}
        />
      </button>
    </div>
  );
}

export function SettingsPage() {
  const queryClient = useQueryClient();
  const { data: profile, isLoading } = useQuery({ queryKey: ['profile'], queryFn: profileApi.get });

  const [prefs, setPrefs] = useState<ProfileUpdate>({});

  useEffect(() => {
    if (!profile) return;
    setPrefs({
      notifyEmail: profile.notifyEmail,
      notifySms: profile.notifySms,
      notifyPush: profile.notifyPush,
      notifyWhatsapp: profile.notifyWhatsapp,
      language: profile.language,
      timezone: profile.timezone,
      theme: profile.theme,
    });
  }, [profile]);

  const save = useMutation({
    mutationFn: () => profileApi.update(prefs),
    onSuccess: (updated: Profile) => queryClient.setQueryData(['profile'], updated),
  });

  const set = (key: keyof ProfileUpdate, value: string | boolean) =>
    setPrefs((p) => ({ ...p, [key]: value }));

  if (isLoading || !profile) {
    return (
      <>
        <PageHeader title="Settings" icon={SlidersHorizontal} />
        <div className="flex items-center gap-2 p-6 text-slate-500">
          <Spinner /> Loading settings…
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Settings"
        subtitle="Notifications, preferences, and account security."
        icon={SlidersHorizontal}
        actions={
          <Button onClick={() => save.mutate()} disabled={save.isPending}>
            {save.isPending ? <Spinner /> : <Save className="h-4 w-4" />} Save
          </Button>
        }
      />
      <div className="space-y-6 p-6">
        {save.isSuccess && (
          <p className="flex items-center gap-2 text-sm text-emerald-600">
            <CheckCircle2 className="h-4 w-4" /> Settings saved.
          </p>
        )}

        {/* Notifications */}
        <Card>
          <h3 className="mb-2 flex items-center gap-2 font-semibold text-slate-800">
            <Bell className="h-4 w-4 text-teal-600" /> Notifications
          </h3>
          <p className="mb-2 text-sm text-slate-500">
            Choose how you want to receive reminders and alerts.
          </p>
          <div className="divide-y divide-slate-100">
            <Toggle label="Email" hint="Diagnosis updates, prescriptions, appointments" checked={!!prefs.notifyEmail} onChange={(v) => set('notifyEmail', v)} />
            <Toggle label="SMS" hint="Text-message medication reminders" checked={!!prefs.notifySms} onChange={(v) => set('notifySms', v)} />
            <Toggle label="Push" hint="In-app and browser push notifications" checked={!!prefs.notifyPush} onChange={(v) => set('notifyPush', v)} />
            <Toggle label="WhatsApp" hint="Reminders and alerts on WhatsApp" checked={!!prefs.notifyWhatsapp} onChange={(v) => set('notifyWhatsapp', v)} />
          </div>
        </Card>

        {/* Preferences */}
        <Card>
          <h3 className="mb-4 flex items-center gap-2 font-semibold text-slate-800">
            <SlidersHorizontal className="h-4 w-4 text-teal-600" /> Preferences
          </h3>
          <div className="grid gap-4 sm:grid-cols-3">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Language</span>
              <select value={prefs.language ?? 'en'} onChange={(e) => set('language', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500">
                {LANGUAGES.map((l) => (
                  <option key={l.value} value={l.value}>{l.label}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Timezone</span>
              <select value={prefs.timezone ?? 'UTC'} onChange={(e) => set('timezone', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500">
                {TIMEZONES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Theme</span>
              <select value={prefs.theme ?? 'system'} onChange={(e) => set('theme', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500">
                {THEMES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </label>
          </div>
        </Card>

        {/* Security */}
        <SecurityCard />

        {/* Account / compliance note */}
        <Card className="border-teal-100 bg-teal-50/40">
          <h3 className="mb-1 flex items-center gap-2 font-semibold text-slate-800">
            <ShieldCheck className="h-4 w-4 text-teal-600" /> About your account
          </h3>
          <p className="text-sm text-slate-600">
            Role: <span className="font-medium capitalize">{profile.role}</span> · Member since{' '}
            {new Date(profile.createdAt).toLocaleDateString()}. HomzDoctor is an AI healthcare
            copilot — all AI findings require licensed-clinician review before they drive care.
          </p>
        </Card>
      </div>
    </>
  );
}

function SecurityCard() {
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const change = useMutation({
    mutationFn: () => profileApi.changePassword({ currentPassword: current, newPassword: next }),
    onSuccess: () => {
      setCurrent('');
      setNext('');
      setConfirm('');
      setLocalError(null);
    },
  });

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    if (next.length < 8) {
      setLocalError('New password must be at least 8 characters.');
      return;
    }
    if (next !== confirm) {
      setLocalError('New passwords do not match.');
      return;
    }
    change.mutate();
  };

  const serverError =
    change.isError &&
    // axios error shape
    ((change.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
      'Could not change password.');

  return (
    <Card>
      <h3 className="mb-4 flex items-center gap-2 font-semibold text-slate-800">
        <Lock className="h-4 w-4 text-teal-600" /> Security
      </h3>
      <form onSubmit={submit} className="grid max-w-md gap-4">
        <PasswordInput
          label="Current password"
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          autoComplete="current-password"
          required
        />
        <PasswordInput
          label="New password"
          value={next}
          onChange={(e) => setNext(e.target.value)}
          autoComplete="new-password"
          required
        />
        <PasswordInput
          label="Confirm new password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          autoComplete="new-password"
          required
        />
        {(localError || serverError) && (
          <p className="flex items-center gap-2 text-sm text-red-600">
            <AlertTriangle className="h-4 w-4" /> {localError || serverError}
          </p>
        )}
        {change.isSuccess && (
          <p className="flex items-center gap-2 text-sm text-emerald-600">
            <CheckCircle2 className="h-4 w-4" /> Password updated.
          </p>
        )}
        <div>
          <Button type="submit" disabled={change.isPending}>
            {change.isPending ? <Spinner /> : <Lock className="h-4 w-4" />} Update password
          </Button>
        </div>
      </form>
    </Card>
  );
}
