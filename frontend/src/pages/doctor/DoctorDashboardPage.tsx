import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { ComponentType } from 'react';
import {
  Stethoscope,
  ClipboardList,
  Users,
  CheckCircle2,
  Pill,
  FileText,
  Check,
  X,
  Pencil,
  AlertTriangle,
} from 'lucide-react';
import { doctorsApi } from '../../api';
import type { PendingRecord, ReviewAction } from '../../api/doctors.api';
import { useAuthStore } from '../../store/authStore';
import { PATHS } from '../../routes/paths';
import { formatDate } from '../../lib/utils';
import { Card, Badge, Button, Spinner, Modal, Input } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';
import { cn } from '../../lib/utils';

type StatTone = 'teal' | 'amber' | 'indigo' | 'emerald';
const TONES: Record<StatTone, string> = {
  teal: 'bg-teal-50 text-teal-600',
  amber: 'bg-amber-50 text-amber-600',
  indigo: 'bg-indigo-50 text-indigo-600',
  emerald: 'bg-emerald-50 text-emerald-600',
};

function Stat({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  tone: StatTone;
}) {
  return (
    <Card className="flex items-center gap-4">
      <div className={cn('rounded-xl p-3', TONES[tone])}>
        <Icon className="h-6 w-6" />
      </div>
      <div>
        <p className="text-sm text-slate-500">{label}</p>
        <p className="text-2xl font-bold text-slate-800">{value}</p>
      </div>
    </Card>
  );
}

export function DoctorDashboardPage() {
  const user = useAuthStore((s) => s.user);
  const queryClient = useQueryClient();
  const [target, setTarget] = useState<PendingRecord | null>(null);

  const stats = useQuery({ queryKey: ['doctor', 'dashboard'], queryFn: doctorsApi.dashboard });
  const pending = useQuery({ queryKey: ['doctor', 'pending'], queryFn: doctorsApi.pendingReviews });

  // Guard: only doctors/admins belong here.
  if (user && user.role !== 'doctor' && user.role !== 'admin') {
    return <Navigate to={PATHS.dashboard} replace />;
  }

  const firstName = user?.fullName?.trim().split(' ').slice(-1)[0];
  const list = pending.data ?? [];

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['doctor', 'pending'] });
    queryClient.invalidateQueries({ queryKey: ['doctor', 'dashboard'] });
  };

  return (
    <>
      <PageHeader
        title={firstName ? `Dr. ${firstName}'s console` : 'Doctor console'}
        subtitle="Review AI findings, approve or reject, and oversee patient care."
        icon={Stethoscope}
        actions={<Badge tone="teal">Doctor</Badge>}
      />
      <div className="space-y-6 p-6">
        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Stat icon={ClipboardList} tone="amber" label="Pending reviews" value={stats.data?.pendingReviews ?? '…'} />
          <Stat icon={CheckCircle2} tone="emerald" label="Reviewed" value={stats.data?.reviewedRecords ?? '…'} />
          <Stat icon={Users} tone="teal" label="Patients" value={stats.data?.patients ?? '…'} />
          <Stat icon={Pill} tone="indigo" label="Rx to approve" value={stats.data?.pendingPrescriptions ?? '…'} />
        </div>

        {/* Pending review queue */}
        <Card className="space-y-4">
          <h3 className="flex items-center gap-2 font-semibold text-slate-800">
            <ClipboardList className="h-5 w-5 text-teal-600" /> Review queue
          </h3>

          {pending.isLoading ? (
            <div className="flex items-center gap-2 text-slate-500">
              <Spinner /> Loading review queue…
            </div>
          ) : pending.isError ? (
            <p className="text-sm text-red-600">Failed to load the review queue.</p>
          ) : list.length === 0 ? (
            <div className="rounded-lg bg-slate-50 p-6 text-center text-sm text-slate-500">
              🎉 No records awaiting review. You're all caught up.
            </div>
          ) : (
            <div className="space-y-3">
              {list.map((r) => (
                <div key={r.id} className="flex items-start gap-4 rounded-lg border border-slate-100 p-3">
                  <div className="rounded-lg bg-teal-50 p-2">
                    <FileText className="h-5 w-5 text-teal-600" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="font-semibold text-slate-900">
                        {r.patientName ?? `Patient #${r.patientId}`}
                      </h4>
                      <Badge tone="gray">{r.recordType}</Badge>
                      <Badge tone={r.status === 'pending' ? 'amber' : 'gray'}>{r.status}</Badge>
                      {typeof r.confidenceScore === 'number' && (
                        <Badge tone="teal">AI {Math.round(r.confidenceScore * 100)}%</Badge>
                      )}
                    </div>
                    {r.diagnosis && (
                      <p className="mt-1 text-sm text-slate-700">
                        <span className="font-medium">AI diagnosis:</span> {r.diagnosis}
                      </p>
                    )}
                    {r.findings && <p className="mt-0.5 text-sm text-slate-500">{r.findings}</p>}
                    <p className="mt-1 text-xs text-slate-400">
                      {r.filePath} · {formatDate(r.createdAt)}
                    </p>
                  </div>
                  <Button variant="outline" className="shrink-0" onClick={() => setTarget(r)}>
                    Review
                  </Button>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <ReviewModal record={target} onClose={() => setTarget(null)} onDone={refresh} />
    </>
  );
}

function ReviewModal({
  record,
  onClose,
  onDone,
}: {
  record: PendingRecord | null;
  onClose: () => void;
  onDone: () => void;
}) {
  const [notes, setNotes] = useState('');
  const [diagnosis, setDiagnosis] = useState('');

  const review = useMutation({
    mutationFn: (action: ReviewAction['action']) =>
      doctorsApi.review(record!.id, {
        action,
        notes: notes || undefined,
        diagnosis: diagnosis || undefined,
      }),
    onSuccess: () => {
      onDone();
      close();
    },
  });

  const close = () => {
    setNotes('');
    setDiagnosis('');
    review.reset();
    onClose();
  };

  // Seed the diagnosis field with the AI's suggestion when opening.
  if (record && diagnosis === '' && record.diagnosis && !review.isPending && !review.isSuccess) {
    setDiagnosis(record.diagnosis);
  }

  return (
    <Modal
      open={record !== null}
      onClose={close}
      title={`Review — ${record?.patientName ?? 'patient'}`}
    >
      <div className="space-y-4">
        {record?.findings && (
          <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
            <p className="font-medium text-slate-700">AI findings</p>
            <p>{record.findings}</p>
          </div>
        )}
        <Input
          label="Diagnosis (you can edit the AI's suggestion)"
          value={diagnosis}
          onChange={(e) => setDiagnosis(e.target.value)}
          placeholder="Confirmed diagnosis"
        />
        <label className="block">
          <span className="mb-1 block text-sm font-medium text-slate-700">Clinical notes</span>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Notes for the patient record"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
          />
        </label>

        {review.isError && (
          <p className="flex items-center gap-2 text-sm text-red-600">
            <AlertTriangle className="h-4 w-4" /> Could not submit. Please try again.
          </p>
        )}

        <div className="flex flex-wrap justify-end gap-2 border-t border-slate-100 pt-4">
          <Button
            variant="outline"
            className="text-red-600"
            disabled={review.isPending}
            onClick={() => review.mutate('reject')}
          >
            <X className="h-4 w-4" /> Reject
          </Button>
          <Button variant="outline" disabled={review.isPending} onClick={() => review.mutate('modify')}>
            <Pencil className="h-4 w-4" /> Save changes
          </Button>
          <Button disabled={review.isPending} onClick={() => review.mutate('approve')}>
            {review.isPending ? <Spinner /> : <Check className="h-4 w-4" />} Approve
          </Button>
        </div>
      </div>
    </Modal>
  );
}
