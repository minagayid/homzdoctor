import { Activity, FileText, Pill, CalendarDays } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../components/ui';
import { PageHeader } from '../components/layout/PageHeader';
import { useAuthStore } from '../store/authStore';
import { recordsApi, prescriptionsApi, appointmentsApi } from '../api';
import { QUERY_KEYS } from '../lib/constants';

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const firstName = user?.fullName?.trim().split(' ')[0];

  const records = useQuery({ queryKey: QUERY_KEYS.records, queryFn: recordsApi.list });
  const prescriptions = useQuery({
    queryKey: QUERY_KEYS.prescriptions,
    queryFn: prescriptionsApi.list,
  });
  const appointments = useQuery({
    queryKey: QUERY_KEYS.appointments,
    queryFn: appointmentsApi.list,
  });

  const count = (q: { data?: unknown[]; isLoading: boolean }) =>
    q.isLoading ? '…' : (q.data?.length ?? 0).toString();

  const stats = [
    { label: 'Records', value: count(records), icon: FileText },
    { label: 'Prescriptions', value: count(prescriptions), icon: Pill },
    { label: 'Appointments', value: count(appointments), icon: CalendarDays },
  ];

  return (
    <>
      <PageHeader
        title={firstName ? `Welcome back, ${firstName}` : 'Dashboard'}
        subtitle="Overview of your healthcare activity."
        icon={Activity}
      />
      <div className="p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {stats.map(({ label, value, icon: Icon }) => (
            <Card key={label} className="flex items-center gap-4">
              <Icon className="h-8 w-8 text-teal-600" />
              <div>
                <p className="text-sm text-slate-500">{label}</p>
                <p className="text-xl font-semibold text-slate-800">{value}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}
