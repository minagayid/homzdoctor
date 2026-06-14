import { Card } from '../../components/ui';

export function SettingsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800">Settings</h1>
      <Card>
        <p className="text-slate-600">
          Manage your account, profile, and preferences here. Wire this up to the auth and
          user APIs from <code className="text-teal-600">src/api</code>.
        </p>
      </Card>
    </div>
  );
}
