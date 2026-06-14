import { Link } from 'react-router-dom';
import { Stethoscope } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { apiOrigin } from '../../config/env';
import { QUERY_KEYS } from '../../lib/constants';
import { PATHS } from '../../routes/paths';
import { Badge } from '../ui';

function HealthBadge() {
  const { data, isError, isLoading } = useQuery({
    queryKey: QUERY_KEYS.health,
    queryFn: async () => (await axios.get(`${apiOrigin}/health`)).data as { status: string },
    retry: false,
    refetchInterval: 15000,
  });

  if (isLoading) return <Badge tone="gray">Checking…</Badge>;
  if (isError || data?.status !== 'healthy') return <Badge tone="red">API offline</Badge>;
  return <Badge tone="green">API healthy</Badge>;
}

export function Navbar() {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white">
      <div className="flex items-center justify-between px-6 py-3">
        <Link to={PATHS.landing} className="flex items-center gap-2">
          <div className="rounded-lg bg-teal-600 p-1.5">
            <Stethoscope className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold text-slate-900">
            Homz<span className="text-teal-600">Doctor</span>
          </span>
        </Link>
        <HealthBadge />
      </div>
    </header>
  );
}
