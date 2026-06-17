import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CalendarDays, Plus, X } from 'lucide-react';
import { appointmentsApi } from '../../api';
import type { AppointmentCreate } from '../../api/appointments.api';
import { QUERY_KEYS } from '../../lib/constants';
import { formatDate } from '../../lib/utils';
import { Card, Badge, Button, Input, Spinner } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

const EMPTY_FORM: AppointmentCreate = { reason: '', scheduledTime: '' };

function statusTone(status: string): 'green' | 'amber' | 'red' | 'gray' {
  if (status === 'completed') return 'green';
  if (status === 'scheduled') return 'amber';
  if (status === 'cancelled') return 'red';
  return 'gray';
}

export function AppointmentsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<AppointmentCreate>(EMPTY_FORM);

  const { data: appointments, isLoading, isError } = useQuery({
    queryKey: QUERY_KEYS.appointments,
    queryFn: appointmentsApi.list,
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: QUERY_KEYS.appointments });

  const create = useMutation({
    mutationFn: appointmentsApi.create,
    onSuccess: () => {
      invalidate();
      setForm(EMPTY_FORM);
      setShowForm(false);
    },
  });

  const cancel = useMutation({ mutationFn: appointmentsApi.cancel, onSuccess: invalidate });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.reason.trim() || !form.scheduledTime) return;
    create.mutate(form);
  };

  return (
    <>
      <PageHeader
        title="Appointments"
        subtitle="Schedule and manage your doctor appointments."
        actions={
          <Button onClick={() => setShowForm((s) => !s)}>
            <Plus className="h-4 w-4" /> Book appointment
          </Button>
        }
      />
      <div className="space-y-6 p-6">
      {showForm && (
        <Card>
          <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
            <Input
              label="Reason"
              placeholder="e.g. Follow-up consultation"
              value={form.reason}
              onChange={(e) => setForm({ ...form, reason: e.target.value })}
              required
            />
            <Input
              label="Date & time"
              type="datetime-local"
              value={form.scheduledTime}
              onChange={(e) => setForm({ ...form, scheduledTime: e.target.value })}
              required
            />
            <div className="flex gap-2 sm:col-span-2">
              <Button type="submit" disabled={create.isPending}>
                {create.isPending ? <Spinner /> : null} Schedule
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
            </div>
            {create.isError && (
              <p className="text-sm text-red-600 sm:col-span-2">Could not book the appointment.</p>
            )}
          </form>
        </Card>
      )}

      {isLoading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Spinner /> Loading appointments…
        </div>
      ) : isError ? (
        <Card>
          <p className="text-sm text-red-600">Failed to load appointments.</p>
        </Card>
      ) : !appointments || appointments.length === 0 ? (
        <Card className="text-center text-slate-500">
          No appointments yet. Click <span className="font-medium text-slate-700">Book
          appointment</span> to schedule one.
        </Card>
      ) : (
        <div className="space-y-3">
          {appointments.map((a) => (
            <Card key={a.id} className="flex items-start gap-4">
              <div className="rounded-lg bg-teal-50 p-2">
                <CalendarDays className="h-5 w-5 text-teal-600" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-semibold text-slate-900">{a.reason ?? 'Appointment'}</h3>
                  <Badge tone={statusTone(a.status)}>{a.status}</Badge>
                </div>
                <p className="mt-1 text-sm text-slate-500">{formatDate(a.scheduledTime)}</p>
              </div>
              {a.status === 'scheduled' && (
                <Button
                  variant="outline"
                  onClick={() => cancel.mutate(a.id)}
                  disabled={cancel.isPending}
                >
                  <X className="h-4 w-4" /> Cancel
                </Button>
              )}
            </Card>
          ))}
        </div>
      )}
      </div>
    </>
  );
}
