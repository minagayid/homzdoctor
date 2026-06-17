import { useQuery } from '@tanstack/react-query';
import { MapPin, Phone } from 'lucide-react';
import { pharmaciesApi } from '../../api';
import { QUERY_KEYS } from '../../lib/constants';
import { Card, Badge, Spinner } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

export function PharmaciesPage() {
  const { data: pharmacies, isLoading, isError } = useQuery({
    queryKey: QUERY_KEYS.pharmacies,
    queryFn: () => pharmaciesApi.search(),
  });

  return (
    <>
      <PageHeader
        title="Pharmacies"
        subtitle="Find nearby pharmacies and check availability."
      />
      <div className="space-y-6 p-6">
      {isLoading ? (
        <div className="flex items-center gap-2 text-slate-500">
          <Spinner /> Loading pharmacies…
        </div>
      ) : isError ? (
        <Card>
          <p className="text-sm text-red-600">Failed to load pharmacies.</p>
        </Card>
      ) : !pharmacies || pharmacies.length === 0 ? (
        <Card className="text-center text-slate-500">No pharmacies found.</Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {pharmacies.map((ph) => (
            <Card key={ph.id} className="flex items-start gap-4">
              <div className="rounded-lg bg-teal-50 p-2">
                <MapPin className="h-5 w-5 text-teal-600" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-semibold text-slate-900">{ph.name}</h3>
                  <Badge tone={ph.isOpen ? 'green' : 'gray'}>{ph.isOpen ? 'Open' : 'Closed'}</Badge>
                </div>
                <p className="mt-1 text-sm text-slate-600">{ph.address}</p>
                {ph.phone && (
                  <p className="mt-1 flex items-center gap-1.5 text-sm text-slate-500">
                    <Phone className="h-3.5 w-3.5" /> {ph.phone}
                  </p>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
      </div>
    </>
  );
}
