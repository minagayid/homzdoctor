import { useState } from 'react';
import type { FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { FileText, Plus, Pencil, Trash2 } from 'lucide-react';
import { recordsApi } from '../../api';
import type { MedicalRecordCreate } from '../../api/records.api';
import type { MedicalRecord } from '../../types';
import { QUERY_KEYS } from '../../lib/constants';
import { formatDate } from '../../lib/utils';
import { Button, Card, Input, Badge, Spinner, Modal } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

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

const EMPTY_FORM: MedicalRecordCreate = { recordType: 'xray', filePath: '', findings: '', diagnosis: '' };

export function RecordsPage() {
  const queryClient = useQueryClient();
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<MedicalRecordCreate>(EMPTY_FORM);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<MedicalRecord | null>(null);

  const { data: records, isLoading, isError } = useQuery({
    queryKey: QUERY_KEYS.records,
    queryFn: recordsApi.list,
  });

  const closeForm = () => {
    setFormOpen(false);
    setEditingId(null);
    setForm(EMPTY_FORM);
    setSelectedFile(null);
  };

  const createMutation = useMutation({
    mutationFn: async (payload: MedicalRecordCreate) => {
      const created = await recordsApi.create(payload);
      if (selectedFile) await recordsApi.uploadFile(created.id, selectedFile);
      return created;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.records });
      closeForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: MedicalRecordCreate }) =>
      recordsApi.update(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.records });
      closeForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => recordsApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.records });
      setDeleteTarget(null);
    },
  });

  const startCreate = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setSelectedFile(null);
    setFormOpen(true);
  };

  const startEdit = (r: MedicalRecord) => {
    setEditingId(r.id);
    setForm({
      recordType: r.recordType,
      filePath: r.filePath,
    });
    setFormOpen(true);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (editingId !== null) {
      updateMutation.mutate({ id: editingId, payload: form });
    } else {
      createMutation.mutate(form);
    }
  };

  const isSaving = createMutation.isPending || updateMutation.isPending;
  const saveError = createMutation.isError || updateMutation.isError;

  return (
    <>
      <PageHeader
        title="Medical Records"
        subtitle="Upload and track your imaging, scans, and reports."
        actions={
          <Button onClick={startCreate}>
            <Plus className="h-4 w-4" /> Add record
          </Button>
        }
      />
      <div className="space-y-6 p-6">
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
                <div className="flex shrink-0 items-center gap-1">
                  <Button
                    variant="ghost"
                    className="px-2 py-2"
                    title="Edit record"
                    aria-label="Edit record"
                    onClick={() => startEdit(r)}
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    className="px-2 py-2 text-red-600 hover:bg-red-50"
                    title="Delete record"
                    aria-label="Delete record"
                    onClick={() => setDeleteTarget(r)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Add / Edit modal */}
      <Modal
        open={formOpen}
        onClose={closeForm}
        title={editingId !== null ? 'Edit record' : 'New record'}
      >
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
            label="File name (optional)"
            placeholder="e.g. chest_xray.dcm"
            value={form.filePath}
            onChange={(e) => setForm({ ...form, filePath: e.target.value })}
          />
          {editingId === null && (
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Medical file</span>
              <input
                type="file"
                accept=".dcm,.dicom,.jpg,.jpeg,.png,.webp,.pdf,.nii,.nii.gz"
                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
              <span className="mt-1 block text-xs text-slate-500">
                The file is stored privately under a generated name.
              </span>
            </label>
          )}
          <p className="text-sm text-slate-500 sm:col-span-2">
            Findings and diagnoses are added by the analysis and clinician-review workflow.
          </p>
          {saveError && (
            <p className="text-sm text-red-600 sm:col-span-2">
              Could not save the record. Please try again.
            </p>
          )}
          <div className="flex justify-end gap-2 sm:col-span-2">
            <Button type="button" variant="outline" onClick={closeForm}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? <Spinner /> : null} {editingId !== null ? 'Save changes' : 'Save record'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete confirmation modal */}
      <Modal
        open={deleteTarget !== null}
        onClose={() => (deleteMutation.isPending ? null : setDeleteTarget(null))}
        title="Delete record"
        widthClassName="max-w-md"
        footer={
          <>
            <Button
              variant="outline"
              onClick={() => setDeleteTarget(null)}
              disabled={deleteMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              disabled={deleteMutation.isPending}
              onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
            >
              {deleteMutation.isPending ? <Spinner /> : <Trash2 className="h-4 w-4" />} Delete
            </Button>
          </>
        }
      >
        <p className="text-sm text-slate-600">
          Are you sure you want to delete this{' '}
          <span className="font-medium text-slate-800">
            {deleteTarget ? typeLabel(deleteTarget.recordType) : ''}
          </span>{' '}
          record{deleteTarget?.filePath ? ` (${deleteTarget.filePath})` : ''}? This action cannot be
          undone.
        </p>
        {deleteMutation.isError && (
          <p className="mt-3 text-sm text-red-600">Could not delete the record. Please try again.</p>
        )}
      </Modal>
    </>
  );
}
