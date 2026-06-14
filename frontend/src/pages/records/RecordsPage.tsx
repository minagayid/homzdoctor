import { Card } from '../../components/ui';

export function RecordsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800">Medical Records</h1>
      <Card>
        <p className="text-slate-600">
          Build the records UI here. Use <code className="text-teal-600">recordsApi</code> from{' '}
          <code className="text-teal-600">src/api</code> to create, fetch and upload records.
        </p>
      </Card>
    </div>
  );
}
