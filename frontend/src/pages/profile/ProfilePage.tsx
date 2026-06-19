import { useEffect, useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { UserRound, Stethoscope, Save, CheckCircle2, AlertTriangle, Camera, Trash2 } from 'lucide-react';
import { profileApi } from '../../api';
import type { Profile, ProfileUpdate } from '../../types';
import { useAuthStore } from '../../store/authStore';
import { Button, Card, Input, Badge, Spinner } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

const GENDERS = ['', 'male', 'female', 'other', 'prefer_not_to_say'];

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <Input
      label={label}
      type={type}
      value={value}
      placeholder={placeholder}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

export function ProfilePage() {
  const queryClient = useQueryClient();
  const setUser = useAuthStore((s) => s.setUser);
  const authUser = useAuthStore((s) => s.user);

  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ['profile'],
    queryFn: profileApi.get,
  });

  const [form, setForm] = useState<ProfileUpdate>({});

  // Seed the form once the profile loads.
  useEffect(() => {
    if (!profile) return;
    setForm({
      fullName: profile.fullName,
      phone: profile.phone ?? '',
      gender: profile.gender ?? '',
      dateOfBirth: profile.dateOfBirth ?? '',
      address: profile.address ?? '',
      city: profile.city ?? '',
      country: profile.country ?? '',
      bio: profile.bio ?? '',
      specialty: profile.specialty ?? '',
      licenseNumber: profile.licenseNumber ?? '',
      hospital: profile.hospital ?? '',
      yearsExperience: profile.yearsExperience,
      qualifications: profile.qualifications ?? '',
      consultationFee: profile.consultationFee ?? '',
    });
  }, [profile]);

  const fileRef = useRef<HTMLInputElement>(null);

  // Keep the sidebar avatar/name in sync with the loaded/updated profile.
  const syncAuth = (p: Profile) => {
    if (authUser) setUser({ ...authUser, fullName: p.fullName, avatarUrl: p.avatarUrl });
  };

  useEffect(() => {
    if (profile) syncAuth(profile);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profile?.avatarUrl, profile?.fullName]);

  const save = useMutation({
    mutationFn: () => profileApi.update(form),
    onSuccess: (updated: Profile) => {
      queryClient.setQueryData(['profile'], updated);
      syncAuth(updated);
    },
  });

  const avatarUpload = useMutation({
    mutationFn: (file: File) => profileApi.uploadAvatar(file),
    onSuccess: (updated: Profile) => {
      queryClient.setQueryData(['profile'], updated);
      syncAuth(updated);
    },
  });

  const avatarRemove = useMutation({
    mutationFn: () => profileApi.removeAvatar(),
    onSuccess: (updated: Profile) => {
      queryClient.setQueryData(['profile'], updated);
      syncAuth(updated);
    },
  });

  const set = (key: keyof ProfileUpdate, value: string | number) =>
    setForm((f) => ({ ...f, [key]: value }));

  if (isLoading) {
    return (
      <>
        <PageHeader title="Profile" icon={UserRound} />
        <div className="flex items-center gap-2 p-6 text-slate-500">
          <Spinner /> Loading profile…
        </div>
      </>
    );
  }

  if (isError || !profile) {
    return (
      <>
        <PageHeader title="Profile" icon={UserRound} />
        <div className="p-6">
          <Card>
            <p className="text-sm text-red-600">Failed to load your profile.</p>
          </Card>
        </div>
      </>
    );
  }

  const isDoctor = profile.role === 'doctor';
  const initials = (form.fullName || profile.fullName || 'U')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <>
      <PageHeader
        title="Profile"
        subtitle="Manage your account information."
        icon={UserRound}
        actions={
          <Button onClick={() => save.mutate()} disabled={save.isPending}>
            {save.isPending ? <Spinner /> : <Save className="h-4 w-4" />} Save changes
          </Button>
        }
      />
      <div className="space-y-6 p-6">
        {/* Identity header with avatar upload */}
        <Card className="flex flex-wrap items-center gap-4">
          <div className="relative">
            <div className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-teal-600 text-2xl font-bold text-white">
              {profile.avatarUrl ? (
                <img src={profile.avatarUrl} alt="Profile" className="h-full w-full object-cover" />
              ) : (
                initials
              )}
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) avatarUpload.mutate(f);
                e.target.value = '';
              }}
            />
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={avatarUpload.isPending}
              title="Upload photo"
              className="absolute -bottom-1 -right-1 rounded-full bg-white p-1.5 text-teal-600 shadow ring-1 ring-slate-200 transition hover:bg-teal-50 disabled:opacity-60"
            >
              {avatarUpload.isPending ? <Spinner /> : <Camera className="h-4 w-4" />}
            </button>
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold text-slate-900">
                {form.fullName || profile.fullName}
              </h2>
              <Badge tone={isDoctor ? 'teal' : 'gray'}>
                {isDoctor ? 'Doctor' : profile.role}
              </Badge>
            </div>
            <p className="text-sm text-slate-500">{profile.email}</p>
            <div className="mt-1 flex items-center gap-3 text-xs">
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="font-medium text-teal-600 hover:underline"
              >
                Change photo
              </button>
              {profile.avatarUrl && (
                <button
                  type="button"
                  onClick={() => avatarRemove.mutate()}
                  disabled={avatarRemove.isPending}
                  className="flex items-center gap-1 font-medium text-red-600 hover:underline disabled:opacity-60"
                >
                  <Trash2 className="h-3 w-3" /> Remove
                </button>
              )}
            </div>
            {avatarUpload.isError && (
              <p className="mt-1 text-xs text-red-600">Upload failed. Use an image under 8 MB.</p>
            )}
          </div>
        </Card>

        {save.isSuccess && (
          <p className="flex items-center gap-2 text-sm text-emerald-600">
            <CheckCircle2 className="h-4 w-4" /> Profile saved.
          </p>
        )}
        {save.isError && (
          <p className="flex items-center gap-2 text-sm text-red-600">
            <AlertTriangle className="h-4 w-4" /> Could not save. Please try again.
          </p>
        )}

        {/* Doctor professional details */}
        {isDoctor && (
          <Card>
            <h3 className="mb-4 flex items-center gap-2 font-semibold text-slate-800">
              <Stethoscope className="h-4 w-4 text-teal-600" /> Professional details
            </h3>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Specialty" value={form.specialty ?? ''} onChange={(v) => set('specialty', v)} placeholder="e.g. Radiology" />
              <Field label="Medical license number" value={form.licenseNumber ?? ''} onChange={(v) => set('licenseNumber', v)} placeholder="e.g. PMC-123456" />
              <Field label="Hospital / clinic" value={form.hospital ?? ''} onChange={(v) => set('hospital', v)} placeholder="e.g. City General Hospital" />
              <Field label="Years of experience" type="number" value={form.yearsExperience != null ? String(form.yearsExperience) : ''} onChange={(v) => set('yearsExperience', v === '' ? 0 : Number(v))} placeholder="e.g. 8" />
              <Field label="Consultation fee" value={form.consultationFee ?? ''} onChange={(v) => set('consultationFee', v)} placeholder="e.g. $50" />
              <div className="sm:col-span-2">
                <label className="block">
                  <span className="mb-1 block text-sm font-medium text-slate-700">Qualifications</span>
                  <textarea
                    value={form.qualifications ?? ''}
                    onChange={(e) => set('qualifications', e.target.value)}
                    rows={2}
                    placeholder="e.g. MBBS, FCPS (Radiology)"
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
                  />
                </label>
              </div>
            </div>
          </Card>
        )}

        {/* Personal information */}
        <Card>
          <h3 className="mb-4 font-semibold text-slate-800">Personal information</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Full name" value={form.fullName ?? ''} onChange={(v) => set('fullName', v)} />
            <Input label="Email" value={profile.email} disabled className="bg-slate-50 text-slate-500" />
            <Field label="Phone" value={form.phone ?? ''} onChange={(v) => set('phone', v)} placeholder="e.g. +1 555 0100" />
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Gender</span>
              <select
                value={form.gender ?? ''}
                onChange={(e) => set('gender', e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              >
                {GENDERS.map((g) => (
                  <option key={g} value={g}>
                    {g === '' ? 'Select…' : g.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </label>
            <Field label="Date of birth" type="date" value={form.dateOfBirth ?? ''} onChange={(v) => set('dateOfBirth', v)} />
            <Field label="City" value={form.city ?? ''} onChange={(v) => set('city', v)} />
            <Field label="Country" value={form.country ?? ''} onChange={(v) => set('country', v)} />
            <div className="sm:col-span-2">
              <Field label="Address" value={form.address ?? ''} onChange={(v) => set('address', v)} />
            </div>
            <div className="sm:col-span-2">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">Bio</span>
                <textarea
                  value={form.bio ?? ''}
                  onChange={(e) => set('bio', e.target.value)}
                  rows={3}
                  placeholder="A short description about you"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
                />
              </label>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}
