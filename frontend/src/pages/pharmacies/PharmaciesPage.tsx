import { Card } from '../../components/ui';

export function PharmaciesPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800">Pharmacies</h1>
      <Card>
        <p className="text-slate-600">
          Build the pharmacy finder here. Use{' '}
          <code className="text-teal-600">pharmaciesApi</code> from{' '}
          <code className="text-teal-600">src/api</code> to search, check inventory and place orders.
        </p>
      </Card>
    </div>
  );
}
