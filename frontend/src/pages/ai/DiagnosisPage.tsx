import { useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  ScanLine,
  Upload,
  FileText,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Search,
  RefreshCw,
  Stethoscope,
} from 'lucide-react';
import { aiApi } from '../../api';
import type { DiagnosisResult } from '../../types';
import { Button, Card, Badge, Spinner } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';

const MODALITIES = [
  { value: 'xray', label: 'X-ray' },
  { value: 'ct', label: 'CT scan' },
  { value: 'mri', label: 'MRI' },
  { value: 'lab_report', label: 'Lab report' },
];

const ACCEPT = '.jpg,.jpeg,.png,.webp,.bmp,.tif,.tiff,.pdf';

function confidenceTone(c: number): 'green' | 'amber' | 'red' {
  if (c >= 0.75) return 'green';
  if (c >= 0.4) return 'amber';
  return 'red';
}

function Section({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <h3 className="mb-3 flex items-center gap-2 font-semibold text-slate-800">
        <Icon className="h-4 w-4 text-teal-600" /> {title}
      </h3>
      {children}
    </Card>
  );
}

function List({ items }: { items?: string[] }) {
  if (!items || items.length === 0) {
    return <p className="text-sm text-slate-400">None noted.</p>;
  }
  return (
    <ul className="list-inside list-disc space-y-1 text-sm text-slate-600">
      {items.map((it, i) => (
        <li key={i}>{it}</li>
      ))}
    </ul>
  );
}

function ResultView({ result }: { result: DiagnosisResult }) {
  if (result.error) {
    return (
      <Card>
        <p className="flex items-center gap-2 text-sm text-red-600">
          <AlertTriangle className="h-4 w-4" /> {result.error}
        </p>
      </Card>
    );
  }

  // Triage rejected a non-medical upload — show a clear notice, not a diagnosis.
  if (result.rejected) {
    return (
      <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
        <div className="text-sm text-amber-800">
          <p className="font-semibold">Not a medical document</p>
          <p>{result.message ?? 'Please upload an X-ray, CT, MRI, ultrasound, or a clinical lab report.'}</p>
          {result.document_type && (
            <p className="mt-1 text-xs text-amber-700">Detected: {result.document_type}</p>
          )}
        </div>
      </div>
    );
  }

  const final = result.final_diagnosis ?? {};
  const confidence = result.confidence ?? final.confidence ?? 0;

  return (
    <div className="space-y-4">
      {/* Doctor-review banner — always shown */}
      <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
        <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
        <div className="text-sm text-amber-800">
          <p className="font-semibold">Awaiting doctor review</p>
          <p>{result.disclaimer ?? 'AI decision support only. A licensed clinician must approve this result.'}</p>
        </div>
      </div>

      {result.urgent && (
        <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertTriangle className="h-5 w-5 shrink-0" />
          <span className="font-medium">Potential urgent finding — please seek prompt clinical attention.</span>
        </div>
      )}

      {/* Final impression headline */}
      <Card className="border-teal-100 bg-teal-50/40">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-800">
            <Stethoscope className="h-5 w-5 text-teal-600" /> Final impression
          </h3>
          <div className="flex items-center gap-2">
            <Badge tone="teal">{result.modality}</Badge>
            <Badge tone={confidenceTone(confidence)}>
              Confidence {Math.round(confidence * 100)}%
            </Badge>
          </div>
        </div>
        <p className="mt-2 text-slate-700">
          {final.primary_impression ?? 'No definitive impression produced.'}
        </p>
        {final.final_findings && final.final_findings.length > 0 && (
          <div className="mt-3">
            <p className="mb-1 text-sm font-medium text-slate-700">Reconciled findings</p>
            <List items={final.final_findings} />
          </div>
        )}
        {final.differential_diagnosis && final.differential_diagnosis.length > 0 && (
          <div className="mt-3">
            <p className="mb-1 text-sm font-medium text-slate-700">Differential diagnosis</p>
            <List items={final.differential_diagnosis} />
          </div>
        )}
        {final.recommended_next_steps && final.recommended_next_steps.length > 0 && (
          <div className="mt-3">
            <p className="mb-1 text-sm font-medium text-slate-700">Recommended next steps</p>
            <List items={final.recommended_next_steps} />
          </div>
        )}
        <p className="mt-3 text-xs text-slate-400">
          Model: {result.model} · {result.pages_analyzed ?? 0} page(s) analyzed
        </p>
      </Card>

      {/* The two earlier passes, for transparency */}
      <div className="grid gap-4 md:grid-cols-2">
        <Section title="Pass 1 · First reading" icon={Search}>
          <p className="mb-1 text-sm font-medium text-slate-700">Observations</p>
          <List items={result.draft_diagnosis?.observations} />
          {result.draft_diagnosis?.suspected_conditions &&
            result.draft_diagnosis.suspected_conditions.length > 0 && (
              <div className="mt-3">
                <p className="mb-1 text-sm font-medium text-slate-700">Suspected conditions</p>
                <List
                  items={result.draft_diagnosis.suspected_conditions.map(
                    (s) => `${s.condition} (${s.likelihood})`,
                  )}
                />
              </div>
            )}
          {result.draft_diagnosis?.image_quality && (
            <p className="mt-3 text-xs text-slate-400">
              Image quality: {result.draft_diagnosis.image_quality}
            </p>
          )}
        </Section>

        <Section title="Pass 2 · Second-reader recheck" icon={RefreshCw}>
          {result.recheck?.agreement && (
            <Badge
              tone={
                result.recheck.agreement === 'agree'
                  ? 'green'
                  : result.recheck.agreement === 'disagree'
                    ? 'red'
                    : 'amber'
              }
            >
              {result.recheck.agreement}
            </Badge>
          )}
          <div className="mt-3">
            <p className="mb-1 text-sm font-medium text-slate-700">Unsupported in first reading</p>
            <List items={result.recheck?.unsupported_findings} />
          </div>
          <div className="mt-3">
            <p className="mb-1 text-sm font-medium text-slate-700">Missed findings</p>
            <List items={result.recheck?.missed_findings} />
          </div>
          {result.recheck?.notes && (
            <p className="mt-3 text-sm text-slate-500">{result.recheck.notes}</p>
          )}
        </Section>
      </div>
    </div>
  );
}

export function DiagnosisPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [modality, setModality] = useState('xray');
  const [dragOver, setDragOver] = useState(false);

  const mutation = useMutation({
    mutationFn: () => aiApi.diagnose(file as File, modality),
  });

  const pickFile = (f: File | null) => {
    setFile(f);
    mutation.reset();
  };

  return (
    <>
      <PageHeader
        title="AI Diagnosis"
        subtitle="Upload imaging or lab findings for AI-assisted analysis. Always reviewed by a doctor."
        icon={ScanLine}
      />
      <div className="space-y-6 p-6">
        <Card>
          <div className="grid gap-4 sm:grid-cols-[1fr_auto] sm:items-end">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Study type</span>
              <select
                value={modality}
                onChange={(e) => setModality(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              >
                {MODALITIES.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </label>
            <Button
              onClick={() => mutation.mutate()}
              disabled={!file || mutation.isPending}
              className="h-[42px]"
            >
              {mutation.isPending ? <Spinner /> : <ScanLine className="h-4 w-4" />}
              {mutation.isPending ? 'Analyzing…' : 'Run diagnosis'}
            </Button>
          </div>

          {/* Drop zone */}
          <div
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              pickFile(e.dataTransfer.files?.[0] ?? null);
            }}
            className={`mt-4 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition ${
              dragOver ? 'border-teal-500 bg-teal-50' : 'border-slate-300 hover:border-teal-400'
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept={ACCEPT}
              className="hidden"
              onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
            />
            {file ? (
              <div className="flex items-center gap-2 text-slate-700">
                <FileText className="h-5 w-5 text-teal-600" />
                <span className="font-medium">{file.name}</span>
                <span className="text-xs text-slate-400">
                  ({Math.round(file.size / 1024)} KB)
                </span>
              </div>
            ) : (
              <>
                <Upload className="mb-2 h-7 w-7 text-slate-400" />
                <p className="text-sm font-medium text-slate-600">
                  Click or drag a file here to upload
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  X-ray, CT, MRI (JPG, PNG…) or a lab report PDF
                </p>
              </>
            )}
          </div>

          {mutation.isError && (
            <p className="mt-3 flex items-center gap-2 text-sm text-red-600">
              <AlertTriangle className="h-4 w-4" />
              Analysis failed. Confirm the backend is running and HF_TOKEN is configured.
            </p>
          )}
          {mutation.isSuccess && !mutation.data?.error && !mutation.data?.rejected && (
            <p className="mt-3 flex items-center gap-2 text-sm text-emerald-600">
              <CheckCircle2 className="h-4 w-4" /> Analysis complete — see results below.
            </p>
          )}
        </Card>

        {mutation.data && <ResultView result={mutation.data} />}
      </div>
    </>
  );
}
