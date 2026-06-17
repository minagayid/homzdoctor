import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Pill, CheckCircle2 } from 'lucide-react';
import { prescriptionsApi } from '../../api';
import { QUERY_KEYS } from '../../lib/constants';
import { formatDate } from '../../lib/utils';
import { Card, Badge, Button, Spinner } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

export function PrescriptionsPage() {
  const queryClient = useQueryClient();

  const { data: prescriptions, isLoading, isError } = useQuery({
    queryKey: QUERY_KEYS.prescriptions,
    queryFn: prescriptionsApi.list,
  });

  const approve = useMutation({
    mutationFn: prescriptionsApi.approve,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.prescriptions }),
  });

  return (
    <>
      <PageHeader
        title="Prescriptions"
        subtitle="Doctor-approved prescriptions and medications."
      />
      <div className="space-y-6 p-6">
      {isLoading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Spinner /> Loading prescriptions…
        </div>
      ) : isError ? (
        <Card>
          <p className="text-sm text-red-600">Failed to load prescriptions.</p>
        </Card>
      ) : !prescriptions || prescriptions.length === 0 ? (
        <Card className="text-center text-slate-500">No prescriptions yet.</Card>
      ) : (
        <div className="space-y-3">
          {prescriptions.map((p) => (
            <Card key={p.id} className="flex items-start gap-4">
              <div className="rounded-lg bg-teal-50 p-2">
                <Pill className="h-5 w-5 text-teal-600" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-semibold text-slate-900">Prescription #{p.id}</h3>
                  <Badge tone={p.approved ? 'green' : 'amber'}>
                    {p.approved ? 'Approved' : 'Pending approval'}
                  </Badge>
                </div>
                <ul className="mt-2 space-y-1">
                  {p.medications.map((med, i) => (
                    <li key={i} className="text-sm text-slate-600">
                      <span className="font-medium text-slate-800">
                        {String(med.name ?? 'Medication')}
                      </span>
                      {med.dose ? ` — ${String(med.dose)}` : ''}
                      {med.frequency ? `, ${String(med.frequency)}` : ''}
                      {med.duration ? ` (${String(med.duration)})` : ''}
                    </li>
                  ))}
                </ul>
                <p className="mt-2 text-xs text-slate-400">{formatDate(p.createdAt)}</p>
              </div>
              {!p.approved && (
                <Button
                  variant="outline"
                  onClick={() => approve.mutate(p.id)}
                  disabled={approve.isPending}
                >
                  {approve.isPending ? <Spinner /> : <CheckCircle2 className="h-4 w-4" />}
                  Approve
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
