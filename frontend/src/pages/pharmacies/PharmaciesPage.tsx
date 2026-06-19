import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { MapPin, Phone, Navigation, ShoppingCart, CheckCircle2, AlertTriangle, Pill } from 'lucide-react';
import { pharmaciesApi, prescriptionsApi } from '../../api';
import type { PharmacyResult, OrderResult } from '../../types';
import { Card, Badge, Spinner, Button, Modal } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

type Coords = { lat: number; lon: number };

export function PharmaciesPage() {
  const [coords, setCoords] = useState<Coords | null>(null);
  const [radius, setRadius] = useState(5);
  const [locating, setLocating] = useState(false);
  const [orderTarget, setOrderTarget] = useState<PharmacyResult | null>(null);

  const search = useQuery({
    queryKey: ['pharmacies', 'search', coords?.lat, coords?.lon, radius],
    queryFn: () =>
      pharmaciesApi.search({ lat: coords?.lat, lon: coords?.lon, radius_km: radius }),
  });

  const useMyLocation = () => {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        setLocating(false);
      },
      () => setLocating(false),
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  const result = search.data;
  const pharmacies = result?.pharmacies ?? [];

  return (
    <>
      <PageHeader
        title="Pharmacies"
        subtitle="Find nearby pharmacies and order your approved prescriptions."
        icon={MapPin}
        actions={
          <div className="flex items-center gap-2">
            <select
              value={radius}
              onChange={(e) => setRadius(Number(e.target.value))}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            >
              {[2, 5, 10, 25].map((r) => (
                <option key={r} value={r}>
                  Within {r} km
                </option>
              ))}
            </select>
            <Button variant="outline" onClick={useMyLocation} disabled={locating}>
              {locating ? <Spinner /> : <Navigation className="h-4 w-4" />} Use my location
            </Button>
          </div>
        }
      />
      <div className="space-y-6 p-6">
        {coords && (
          <p className="text-sm text-slate-500">
            Showing pharmacies near {coords.lat.toFixed(3)}, {coords.lon.toFixed(3)} ·{' '}
            <span className="text-slate-400">source: {result?.source ?? '—'}</span>
          </p>
        )}

        {result?.summary && (
          <Card className="border-teal-100 bg-teal-50/40">
            <p className="text-sm text-slate-700">{result.summary}</p>
          </Card>
        )}

        {search.isLoading ? (
          <div className="flex items-center gap-2 text-slate-500">
            <Spinner /> Loading pharmacies…
          </div>
        ) : search.isError ? (
          <Card>
            <p className="text-sm text-red-600">Failed to load pharmacies.</p>
          </Card>
        ) : pharmacies.length === 0 ? (
          <Card className="text-center text-slate-500">No pharmacies found in this area.</Card>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {pharmacies.map((ph, i) => (
              <Card key={ph.id ?? ph.place_id ?? i} className="flex items-start gap-4">
                <div className="rounded-lg bg-teal-50 p-2">
                  <MapPin className="h-5 w-5 text-teal-600" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-slate-900">{ph.name}</h3>
                    {ph.is_open != null && (
                      <Badge tone={ph.is_open ? 'green' : 'gray'}>
                        {ph.is_open ? 'Open' : 'Closed'}
                      </Badge>
                    )}
                    {ph.distance_km != null && <Badge tone="teal">{ph.distance_km} km</Badge>}
                  </div>
                  {ph.address && <p className="mt-1 text-sm text-slate-600">{ph.address}</p>}
                  {ph.phone && (
                    <p className="mt-1 flex items-center gap-1.5 text-sm text-slate-500">
                      <Phone className="h-3.5 w-3.5" /> {ph.phone}
                    </p>
                  )}
                  {ph.id != null && (
                    <Button
                      variant="outline"
                      className="mt-3 px-3 py-1.5 text-xs"
                      onClick={() => setOrderTarget(ph)}
                    >
                      <ShoppingCart className="h-3.5 w-3.5" /> Order prescription
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <OrderModal pharmacy={orderTarget} onClose={() => setOrderTarget(null)} />
    </>
  );
}

/** Two-step ordering: preview the order, then confirm. */
function OrderModal({
  pharmacy,
  onClose,
}: {
  pharmacy: PharmacyResult | null;
  onClose: () => void;
}) {
  const [prescriptionId, setPrescriptionId] = useState<number | null>(null);
  const [confirmed, setConfirmed] = useState(false);

  const prescriptions = useQuery({
    queryKey: ['prescriptions'],
    queryFn: prescriptionsApi.list,
    enabled: pharmacy != null,
  });

  const order = useMutation({
    mutationFn: (patientConfirmed: boolean) =>
      pharmaciesApi.order(pharmacy!.id as number, {
        prescription_id: prescriptionId as number,
        patient_confirmed: patientConfirmed,
      }),
  });

  const close = () => {
    setPrescriptionId(null);
    setConfirmed(false);
    order.reset();
    onClose();
  };

  const approved = (prescriptions.data ?? []).filter((p) => p.approved);
  const data: OrderResult | undefined = order.data;
  const placed = data?.order_placed === true;
  const items = data?.items ?? data?.order_preview ?? [];

  return (
    <Modal open={pharmacy != null} onClose={close} title={`Order at ${pharmacy?.name ?? ''}`}>
      {placed ? (
        <div className="space-y-3">
          <p className="flex items-center gap-2 font-medium text-emerald-600">
            <CheckCircle2 className="h-5 w-5" /> Order submitted
          </p>
          <p className="text-sm text-slate-600">{data?.confirmation_message}</p>
          <div className="flex justify-end">
            <Button onClick={close}>Done</Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">
              Doctor-approved prescription
            </span>
            {prescriptions.isLoading ? (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Spinner /> Loading…
              </div>
            ) : approved.length === 0 ? (
              <p className="text-sm text-amber-600">
                You have no doctor-approved prescriptions to order yet.
              </p>
            ) : (
              <select
                value={prescriptionId ?? ''}
                onChange={(e) => {
                  setPrescriptionId(Number(e.target.value));
                  setConfirmed(false);
                  order.reset();
                }}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              >
                <option value="" disabled>
                  Select a prescription…
                </option>
                {approved.map((p) => (
                  <option key={p.id} value={p.id}>
                    #{p.id} · {p.medications.map((m) => (m as { name?: string }).name).join(', ')}
                  </option>
                ))}
              </select>
            )}
          </label>

          {/* Order preview */}
          {items.length > 0 && (
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p className="mb-2 text-sm font-medium text-slate-700">Order summary</p>
              <ul className="space-y-1 text-sm text-slate-600">
                {items.map((it, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <Pill className="h-3.5 w-3.5 text-teal-600" />
                    {it.name}
                    {it.dose ? ` · ${it.dose}` : ''}
                    {it.frequency ? ` · ${it.frequency}` : ''}
                    {it.duration ? ` · ${it.duration}` : ''}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {order.data?.error && !order.data.requires_confirmation && (
            <p className="flex items-center gap-2 text-sm text-red-600">
              <AlertTriangle className="h-4 w-4" /> {order.data.error}
            </p>
          )}

          {/* Confirmation gate */}
          {items.length > 0 && (
            <label className="flex items-start gap-2 text-sm text-slate-600">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
                className="mt-0.5"
              />
              I confirm I want to order these medications at {pharmacy?.name}.
            </label>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={close}>
              Cancel
            </Button>
            {items.length === 0 ? (
              <Button
                disabled={!prescriptionId || order.isPending}
                onClick={() => order.mutate(false)}
              >
                {order.isPending ? <Spinner /> : null} Preview order
              </Button>
            ) : (
              <Button disabled={!confirmed || order.isPending} onClick={() => order.mutate(true)}>
                {order.isPending ? <Spinner /> : <ShoppingCart className="h-4 w-4" />} Place order
              </Button>
            )}
          </div>
        </div>
      )}
    </Modal>
  );
}
