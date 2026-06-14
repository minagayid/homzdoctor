import { Activity, FileText, Pill, MapPin } from 'lucide-react';
import { Card } from '../components/ui';

const stats = [
  { label: 'Records', value: '—', icon: FileText },
  { label: 'Prescriptions', value: '—', icon: Pill },
  { label: 'Pharmacies', value: '—', icon: MapPin },
];

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold text-slate-800">
          <Activity className="h-6 w-6 text-teal-600" /> Dashboard
        </h1>
        <p className="mt-1 text-slate-600">Overview of your healthcare activity.</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {stats.map(({ label, value, icon: Icon }) => (
          <Card key={label} className="flex items-center gap-4">
            <Icon className="h-8 w-8 text-teal-600" />
            <div>
              <p className="text-sm text-slate-500">{label}</p>
              <p className="text-xl font-semibold text-slate-800">{value}</p>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
