import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Stethoscope, ShieldCheck, Brain, Lock } from 'lucide-react';
import { PATHS } from '../../routes/paths';

const highlights = [
  { icon: ShieldCheck, text: 'Every AI finding reviewed by a licensed doctor' },
  { icon: Brain, text: 'AI diagnostics for scans, labs, and symptoms' },
  { icon: Lock, text: 'HIPAA-aligned, end-to-end encrypted' },
];

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen bg-white">
      {/* Left brand panel */}
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-gradient-to-br from-teal-600 to-teal-800 p-10 text-white lg:flex">
        <Link to={PATHS.landing} className="flex items-center gap-2">
          <div className="rounded-lg bg-white/15 p-1.5">
            <Stethoscope className="h-5 w-5" />
          </div>
          <span className="text-lg font-semibold">
            Homz<span className="text-teal-200">Doctor</span>
          </span>
        </Link>

        <div>
          <h2 className="text-3xl font-bold leading-tight">
            AI-powered care, with a doctor's final say.
          </h2>
          <p className="mt-3 max-w-sm text-teal-100">
            Clinical-grade insights from home — reviewed by licensed physicians.
          </p>
          <ul className="mt-8 space-y-4">
            {highlights.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-3">
                <div className="rounded-lg bg-white/15 p-2">
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-sm text-teal-50">{text}</span>
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-teal-200/80">
          Not for emergencies — call your local emergency number.
        </p>

        {/* Decorative glow */}
        <div className="pointer-events-none absolute -right-12 top-1/3 h-48 w-48 rounded-full bg-white/10 blur-3xl" />
      </div>

      {/* Right form area */}
      <div className="flex w-full flex-col lg:w-1/2">
        <div className="flex items-center justify-between p-6">
          <Link
            to={PATHS.landing}
            className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 transition hover:text-teal-600"
          >
            <ArrowLeft className="h-4 w-4" /> Back to home
          </Link>
          {/* Mobile logo (brand panel is hidden on small screens) */}
          <Link to={PATHS.landing} className="flex items-center gap-2 lg:hidden">
            <Stethoscope className="h-5 w-5 text-teal-600" />
            <span className="font-semibold text-slate-900">
              Homz<span className="text-teal-600">Doctor</span>
            </span>
          </Link>
        </div>

        <div className="flex flex-1 items-center justify-center px-6 pb-12">
          <div className="w-full max-w-sm">
            <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
            <p className="mb-6 mt-1 text-sm text-slate-500">{subtitle}</p>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
