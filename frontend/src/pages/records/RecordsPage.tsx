import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { FileText, Plus } from 'lucide-react';
import { recordsApi } from '../../api';
import type { MedicalRecordCreate } from '../../api/records.api';
import { QUERY_KEYS } from '../../lib/constants';
import { formatDate } from '../../lib/utils';
import { Button, Card, Input, Badge, Spinner } from '../../components/ui';

const RECORD_TYPES = [
  { value: 'xray', label: 'X-ray' },
  { value: 'mri', label: 'MRI' },
  { value: 'ct', label: 'CT scan' },
  { value: 'lab_report', label: 'Lab report' },
];

const typeLabel = (t: string) => RECORD_TYPES.find((r) => r.value === t)?.label ?? t;

function statusTone(status: string): 'green' | 'amber' | 'gray' {
  if (status === 'reviewed' || status === 'approved') return 'green';
  if (status === 'pending') return 'amber';
  return 'gray';
}

const EMPTY_FORM: MedicalRecordCreate = { recordType: 'xray', filePath: '' };

export function RecordsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<MedicalRecordCreate>(EMPTY_FORM);

  const { data: records, isLoading, isError } = useQuery({
    queryKey: QUERY_KEYS.records,
    queryFn: recordsApi.list,
  });

  const createMutation = useMutation({
    mutationFn: recordsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.records });
      setForm(EMPTY_FORM);
      setShowForm(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.filePath.trim()) return;
    createMutation.mutate(form);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Medical Records</h1>
          <p className="mt-1 text-slate-600">Upload and track your imaging, scans, and reports.</p>
        </div>
        <Button onClick={() => setShowForm((s) => !s)}>
          <Plus className="h-4 w-4" /> Add record
        </Button>
      </div>

      {showForm && (
        <Card>
          <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Record type</span>
              <select
                value={form.recordType}
                onChange={(e) => setForm({ ...form, recordType: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              >
                {RECORD_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>
            <Input
              label="File name"
              placeholder="e.g. chest_xray.dcm"
              value={form.filePath}
              onChange={(e) => setForm({ ...form, filePath: e.target.value })}
              required
            />
            <div className="sm:col-span-2">
              <Input
                label="Findings (optional)"
                placeholder="Notes or symptoms"
                value={form.findings ?? ''}
                onChange={(e) => setForm({ ...form, findings: e.target.value })}
              />
            </div>
            <div className="flex gap-2 sm:col-span-2">
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? <Spinner /> : null} Save record
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
            </div>
            {createMutation.isError && (
              <p className="text-sm text-red-600 sm:col-span-2">
                Could not save the record. Please try again.
              </p>
            )}
          </form>
        </Card>
      )}

      {isLoading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Spinner /> Loading records…
        </div>
      ) : isError ? (
        <Card>
          <p className="text-sm text-red-600">
            Failed to load records. Make sure you're signed in and the backend is running.
          </p>
        </Card>
      ) : !records || records.length === 0 ? (
        <Card className="text-center text-slate-500">
          No records yet. Click <span className="font-medium text-slate-700">Add record</span> to
          create one.
        </Card>
      ) : (
        <div className="space-y-3">
          {records.map((r) => (
            <Card key={r.id} className="flex items-start gap-4">
              <div className="rounded-lg bg-teal-50 p-2">
                <FileText className="h-5 w-5 text-teal-600" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-semibold text-slate-900">{typeLabel(r.recordType)}</h3>
                  <Badge tone={statusTone(r.status)}>{r.status}</Badge>
                  {r.doctorReviewed && <Badge tone="teal">Doctor reviewed</Badge>}
                </div>
                <p className="truncate text-sm text-slate-500">{r.filePath}</p>
                {r.findings && <p className="mt-2 text-sm text-slate-600">{r.findings}</p>}
                {r.diagnosis && (
                  <p className="mt-1 text-sm text-slate-600">
                    <span className="font-medium text-slate-700">Diagnosis:</span> {r.diagnosis}
                  </p>
                )}
                <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-400">
                  <span>{formatDate(r.createdAt)}</span>
                  {typeof r.confidenceScore === 'number' && (
                    <span>AI confidence {Math.round(r.confidenceScore * 100)}%</span>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
