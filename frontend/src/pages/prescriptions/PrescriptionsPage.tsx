import { Card } from '../../components/ui';

export function PrescriptionsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800">Prescriptions</h1>
      <Card>
        <p className="text-slate-600">
          Build the prescriptions UI here. Use{' '}
          <code className="text-teal-600">prescriptionsApi</code> from{' '}
          <code className="text-teal-600">src/api</code> to create, fetch and approve prescriptions.
        </p>
      </Card>
    </div>
  );
}
