import { Link } from 'react-router-dom';
import { PATHS } from '../routes/paths';

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50">
      <h1 className="text-4xl font-bold text-slate-800">404</h1>
      <p className="text-slate-600">Page not found.</p>
      <Link to={PATHS.dashboard} className="text-teal-600 hover:underline">
        Go to dashboard
      </Link>
    </div>
  );
}
