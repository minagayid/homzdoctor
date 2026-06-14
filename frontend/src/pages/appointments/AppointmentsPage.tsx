import { Card } from '../../components/ui';

export function AppointmentsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800">Appointments</h1>
      <Card>
        <p className="text-slate-600">
          Build the appointments UI here. Use{' '}
          <code className="text-teal-600">appointmentsApi</code> from{' '}
          <code className="text-teal-600">src/api</code> to schedule, fetch and cancel appointments.
        </p>
      </Card>
    </div>
  );
}
