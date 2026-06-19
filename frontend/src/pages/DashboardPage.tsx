import type { ComponentType } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  FileText,
  Pill,
  CalendarDays,
  Bot,
  Sparkles,
  Video,
  Bell,
  TrendingUp,
  ShieldCheck,
  Clock,
  ArrowRight,
  Plus,
} from 'lucide-react';
import { Card, Badge, Spinner } from '../components/ui';
import { PageHeader } from '../components/layout/PageHeader';
import { useAuthStore } from '../store/authStore';
import { recordsApi, prescriptionsApi, appointmentsApi } from '../api';
import { QUERY_KEYS } from '../lib/constants';
import { PATHS } from '../routes/paths';
import { formatDate } from '../lib/utils';
import { cn } from '../lib/utils';
import type { Appointment, MedicalRecord } from '../types';

type StatTone = 'teal' | 'indigo' | 'amber' | 'emerald';

const STAT_TONES: Record<StatTone, string> = {
  teal: 'bg-teal-50 text-teal-600',
  indigo: 'bg-indigo-50 text-indigo-600',
  amber: 'bg-amber-50 text-amber-600',
  emerald: 'bg-emerald-50 text-emerald-600',
};

function StatCard({
  icon: Icon,
  label,
  value,
  sublabel,
  tone,
  to,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  sublabel?: string;
  tone: StatTone;
  to: string;
}) {
  return (
    <Link to={to} className="group">
      <Card className="flex items-center gap-4 transition group-hover:border-teal-200 group-hover:shadow-md">
        <div className={cn('rounded-xl p-3', STAT_TONES[tone])}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="min-w-0">
          <p className="text-sm text-slate-500">{label}</p>
          <p className="text-2xl font-bold text-slate-800">{value}</p>
          {sublabel && <p className="text-xs text-slate-400">{sublabel}</p>}
        </div>
      </Card>
    </Link>
  );
}

const COMING_SOON = [
  {
    icon: Sparkles,
    title: 'AI Imaging Diagnostics',
    desc: 'Instant AI analysis of X-rays, MRIs & CT scans with doctor sign-off.',
  },
  {
    icon: Video,
    title: 'Video Consultations',
    desc: 'Talk to your doctor face-to-face from anywhere, anytime.',
  },
  {
    icon: Bell,
    title: 'Smart Medication Reminders',
    desc: 'Timely alerts so you never miss a dose, with adherence tracking.',
  },
  {
    icon: TrendingUp,
    title: 'Health Insights & Trends',
    desc: 'Track vitals and recovery progress over time with visual reports.',
  },
];

export function DashboardPage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const isDoctor = user?.role === 'doctor';
  const firstName = user?.fullName?.trim().split(' ')[0];

  // Doctors get their own dashboard — send them there.
  if (isDoctor) return <Navigate to={PATHS.doctor} replace />;

  const records = useQuery({ queryKey: QUERY_KEYS.records, queryFn: recordsApi.list });
  const prescriptions = useQuery({
    queryKey: QUERY_KEYS.prescriptions,
    queryFn: prescriptionsApi.list,
  });
  const appointments = useQuery({
    queryKey: QUERY_KEYS.appointments,
    queryFn: appointmentsApi.list,
  });

  const isLoading = records.isLoading || prescriptions.isLoading || appointments.isLoading;

  const recordList: MedicalRecord[] = records.data ?? [];
  const rxList = prescriptions.data ?? [];
  const apptList: Appointment[] = appointments.data ?? [];

  const now = Date.now();
  const pendingRecords = recordList.filter((r) => r.status === 'pending').length;
  const reviewedRecords = recordList.filter((r) => r.doctorReviewed).length;
  const reviewedPct = recordList.length ? Math.round((reviewedRecords / recordList.length) * 100) : 0;
  const pendingRx = rxList.filter((p) => !p.approved).length;

  const upcoming = apptList
    .filter((a) => a.status === 'scheduled' && new Date(a.scheduledTime).getTime() >= now)
    .sort((a, b) => new Date(a.scheduledTime).getTime() - new Date(b.scheduledTime).getTime());
  const nextAppt = upcoming[0];

  const recentRecords = [...recordList]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 4);

  const num = (q: { isLoading: boolean }, v: string | number) => (q.isLoading ? '…' : v);

  const today = new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  return (
    <>
      <PageHeader
        title={firstName ? `Welcome back, ${firstName}` : 'Dashboard'}
        subtitle="Overview of your healthcare activity."
        icon={Activity}
        actions={<Badge tone="teal">{isDoctor ? 'Doctor' : 'Patient'}</Badge>}
      />

      <div className="space-y-6 p-6">
        {/* Hero banner */}
        <div className="overflow-hidden rounded-2xl bg-gradient-to-br from-teal-600 to-emerald-500 p-6 text-white shadow-sm sm:p-8">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="min-w-0">
              <p className="text-sm text-teal-50">{today}</p>
              <h2 className="mt-1 text-2xl font-bold">
                {isDoctor ? 'Your patients at a glance' : 'Your health, all in one place'}
              </h2>
              <p className="mt-1 max-w-xl text-teal-50">
                {isDoctor
                  ? 'Review AI findings, approve prescriptions, and manage appointments — with doctor oversight built in.'
                  : 'Doctor-reviewed AI care. Track records, prescriptions, and appointments in one secure place.'}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Link
                to={PATHS.appointments}
                className="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-teal-700 shadow-sm transition hover:bg-teal-50"
              >
                <CalendarDays className="h-4 w-4" /> Book appointment
              </Link>
              <Link
                to={PATHS.chat}
                className="inline-flex items-center gap-2 rounded-lg border border-white/40 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                <Bot className="h-4 w-4" /> Ask assistant
              </Link>
            </div>
          </div>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={FileText}
            tone="teal"
            label="Records"
            value={num(records, recordList.length)}
            sublabel={pendingRecords ? `${pendingRecords} pending analysis` : 'All processed'}
            to={PATHS.records}
          />
          <StatCard
            icon={Pill}
            tone="indigo"
            label="Prescriptions"
            value={num(prescriptions, rxList.length)}
            sublabel={pendingRx ? `${pendingRx} awaiting approval` : 'All approved'}
            to={PATHS.prescriptions}
          />
          <StatCard
            icon={CalendarDays}
            tone="amber"
            label="Upcoming appointments"
            value={num(appointments, upcoming.length)}
            sublabel={nextAppt ? `Next: ${formatDate(nextAppt.scheduledTime)}` : 'None scheduled'}
            to={PATHS.appointments}
          />
          <StatCard
            icon={ShieldCheck}
            tone="emerald"
            label="Doctor-reviewed"
            value={num(records, `${reviewedPct}%`)}
            sublabel={`${reviewedRecords} of ${recordList.length} records`}
            to={PATHS.records}
          />
        </div>

        {/* Two-column: upcoming appointments + recent records */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="flex items-center gap-2 font-semibold text-slate-800">
                <CalendarDays className="h-5 w-5 text-teal-600" /> Upcoming appointments
              </h3>
              <Link
                to={PATHS.appointments}
                className="inline-flex items-center gap-1 text-sm font-medium text-teal-600 hover:underline"
              >
                View all <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
            {isLoading ? (
              <div className="flex items-center gap-2 text-slate-500">
                <Spinner /> Loading…
              </div>
            ) : upcoming.length === 0 ? (
              <div className="rounded-lg bg-slate-50 p-4 text-center text-sm text-slate-500">
                No upcoming appointments.{' '}
                <Link to={PATHS.appointments} className="font-medium text-teal-600 hover:underline">
                  Book one
                </Link>
                .
              </div>
            ) : (
              <ul className="space-y-2">
                {upcoming.slice(0, 4).map((a) => (
                  <li
                    key={a.id}
                    className="flex items-center gap-3 rounded-lg border border-slate-100 p-3"
                  >
                    <div className="rounded-lg bg-amber-50 p-2">
                      <Clock className="h-4 w-4 text-amber-600" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-slate-800">
                        {a.reason ?? 'Appointment'}
                      </p>
                      <p className="text-xs text-slate-500">{formatDate(a.scheduledTime)}</p>
                    </div>
                    <Badge tone="amber">{a.status}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="flex items-center gap-2 font-semibold text-slate-800">
                <FileText className="h-5 w-5 text-teal-600" /> Recent records
              </h3>
              <Link
                to={PATHS.records}
                className="inline-flex items-center gap-1 text-sm font-medium text-teal-600 hover:underline"
              >
                View all <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
            {isLoading ? (
              <div className="flex items-center gap-2 text-slate-500">
                <Spinner /> Loading…
              </div>
            ) : recentRecords.length === 0 ? (
              <div className="rounded-lg bg-slate-50 p-4 text-center text-sm text-slate-500">
                No records yet.{' '}
                <Link to={PATHS.records} className="font-medium text-teal-600 hover:underline">
                  Add one
                </Link>
                .
              </div>
            ) : (
              <ul className="space-y-2">
                {recentRecords.map((r) => (
                  <li
                    key={r.id}
                    className="flex items-center gap-3 rounded-lg border border-slate-100 p-3"
                  >
                    <div className="rounded-lg bg-teal-50 p-2">
                      <FileText className="h-4 w-4 text-teal-600" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-slate-800">{r.filePath}</p>
                      <p className="text-xs text-slate-500">{formatDate(r.createdAt)}</p>
                    </div>
                    <Badge tone={r.status === 'pending' ? 'amber' : 'green'}>{r.status}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>

        {/* Care progress */}
        <Card className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Care progress</h3>
            <span className="text-sm font-semibold text-teal-600">{reviewedPct}%</span>
          </div>
          <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-gradient-to-r from-teal-500 to-emerald-500 transition-all"
              style={{ width: `${reviewedPct}%` }}
            />
          </div>
          <p className="text-sm text-slate-500">
            {reviewedRecords} of {recordList.length || 0} records have been reviewed by a doctor.
          </p>
        </Card>

        {/* Coming soon / future features */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-teal-600" />
            <h3 className="text-lg font-semibold text-slate-800">Coming soon</h3>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {COMING_SOON.map(({ icon: Icon, title, desc }) => (
              <Card key={title} className="relative space-y-3">
                <Badge tone="teal" className="absolute right-4 top-4">
                  Soon
                </Badge>
                <div className="inline-flex rounded-xl bg-teal-50 p-3">
                  <Icon className="h-6 w-6 text-teal-600" />
                </div>
                <h4 className="font-semibold text-slate-800">{title}</h4>
                <p className="text-sm text-slate-500">{desc}</p>
              </Card>
            ))}
          </div>
        </div>

        {/* Quick add for patients */}
        {!isDoctor && (
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => navigate(PATHS.records)}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              <Plus className="h-4 w-4" /> Add a record
            </button>
            <button
              type="button"
              onClick={() => navigate(PATHS.pharmacies)}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              <Pill className="h-4 w-4" /> Find a pharmacy
            </button>
          </div>
        )}
      </div>
    </>
  );
}
