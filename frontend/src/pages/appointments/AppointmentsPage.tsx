import { useState } from 'react';
import type { FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CalendarDays, Plus, X, Pencil, Trash2, CalendarClock } from 'lucide-react';
import { appointmentsApi } from '../../api';
import type { AppointmentCreate } from '../../api/appointments.api';
import type { Appointment } from '../../types';
import { QUERY_KEYS } from '../../lib/constants';
import { formatDate } from '../../lib/utils';
import { Card, Badge, Button, Input, Spinner, Modal } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

const EMPTY_FORM: AppointmentCreate = { reason: '', scheduledTime: '' };

function statusTone(status: string): 'green' | 'amber' | 'red' | 'gray' {
  if (status === 'completed') return 'green';
  if (status === 'scheduled') return 'amber';
  if (status === 'cancelled') return 'red';
  return 'gray';
}

/** ISO string -> value for a <input type="datetime-local"> (local time, no seconds). */
function toLocalInput(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const tzOffset = d.getTimezoneOffset() * 60000;
  return new Date(d.getTime() - tzOffset).toISOString().slice(0, 16);
}

export function AppointmentsPage() {
  const queryClient = useQueryClient();
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Appointment | null>(null);
  const [form, setForm] = useState<AppointmentCreate>(EMPTY_FORM);
  const [deleteTarget, setDeleteTarget] = useState<Appointment | null>(null);

  const { data: appointments, isLoading, isError } = useQuery({
    queryKey: QUERY_KEYS.appointments,
    queryFn: appointmentsApi.list,
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: QUERY_KEYS.appointments });

  const closeForm = () => {
    setFormOpen(false);
    setEditing(null);
    setForm(EMPTY_FORM);
  };

  const create = useMutation({
    mutationFn: appointmentsApi.create,
    onSuccess: () => {
      invalidate();
      closeForm();
    },
  });

  const update = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: AppointmentCreate }) =>
      appointmentsApi.update(id, payload),
    onSuccess: () => {
      invalidate();
      closeForm();
    },
  });

  const cancel = useMutation({ mutationFn: appointmentsApi.cancel, onSuccess: invalidate });

  const remove = useMutation({
    mutationFn: (id: number) => appointmentsApi.remove(id),
    onSuccess: () => {
      invalidate();
      setDeleteTarget(null);
    },
  });

  const startCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormOpen(true);
  };

  const startEdit = (a: Appointment) => {
    setEditing(a);
    setForm({ reason: a.reason ?? '', scheduledTime: toLocalInput(a.scheduledTime) });
    setFormOpen(true);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!form.reason.trim() || !form.scheduledTime) return;
    if (editing) {
      update.mutate({ id: editing.id, payload: form });
    } else {
      create.mutate(form);
    }
  };

  const isSaving = create.isPending || update.isPending;
  const saveError = create.isError || update.isError;

  return (
    <>
      <PageHeader
        title="Appointments"
        subtitle="Schedule and manage your doctor appointments."
        icon={CalendarDays}
        actions={
          <Button onClick={startCreate}>
            <Plus className="h-4 w-4" /> Book appointment
          </Button>
        }
      />
      <div className="space-y-6 p-6">
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
            No appointments yet. Click{' '}
            <span className="font-medium text-slate-700">Book appointment</span> to schedule one.
          </Card>
        ) : (
          <div className="space-y-3">
            {appointments.map((a) => {
              const isScheduled = a.status === 'scheduled';
              return (
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
                  <div className="flex shrink-0 items-center gap-1">
                    {isScheduled && (
                      <>
                        <Button
                          variant="ghost"
                          className="px-2 py-2"
                          title="Reschedule / edit"
                          aria-label="Edit appointment"
                          onClick={() => startEdit(a)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          className="px-2 py-2 text-amber-600 hover:bg-amber-50"
                          title="Cancel appointment"
                          aria-label="Cancel appointment"
                          onClick={() => cancel.mutate(a.id)}
                          disabled={cancel.isPending}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </>
                    )}
                    <Button
                      variant="ghost"
                      className="px-2 py-2 text-red-600 hover:bg-red-50"
                      title="Delete appointment"
                      aria-label="Delete appointment"
                      onClick={() => setDeleteTarget(a)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Book / edit modal */}
      <Modal
        open={formOpen}
        onClose={closeForm}
        title={editing ? 'Reschedule appointment' : 'Book appointment'}
      >
        <form onSubmit={handleSubmit} className="grid gap-4">
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
          {saveError && (
            <p className="text-sm text-red-600">Could not save the appointment. Please try again.</p>
          )}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={closeForm}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? <Spinner /> : <CalendarClock className="h-4 w-4" />}
              {editing ? 'Save changes' : 'Schedule'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete confirmation */}
      <Modal
        open={deleteTarget !== null}
        onClose={() => (remove.isPending ? null : setDeleteTarget(null))}
        title="Delete appointment"
        widthClassName="max-w-md"
        footer={
          <>
            <Button variant="outline" onClick={() => setDeleteTarget(null)} disabled={remove.isPending}>
              Cancel
            </Button>
            <Button
              variant="danger"
              disabled={remove.isPending}
              onClick={() => deleteTarget && remove.mutate(deleteTarget.id)}
            >
              {remove.isPending ? <Spinner /> : <Trash2 className="h-4 w-4" />} Delete
            </Button>
          </>
        }
      >
        <p className="text-sm text-slate-600">
          Are you sure you want to permanently delete{' '}
          <span className="font-medium text-slate-800">{deleteTarget?.reason ?? 'this appointment'}</span>
          {deleteTarget ? ` (${formatDate(deleteTarget.scheduledTime)})` : ''}? This action cannot be
          undone.
        </p>
        {remove.isError && (
          <p className="mt-3 text-sm text-red-600">Could not delete the appointment. Please try again.</p>
        )}
      </Modal>
    </>
  );
}
