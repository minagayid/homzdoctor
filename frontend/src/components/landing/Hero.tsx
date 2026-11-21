import { Link } from 'react-router-dom';
import { Shield, Microscope, Sparkles, Brain, ShieldCheck, Activity } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-white py-20 md:py-28">
      {/* Ambient brand mesh background */}
      <div className="pointer-events-none absolute inset-0 -z-10 bg-mesh" />
      <div className="pointer-events-none absolute -top-24 left-1/2 -z-10 h-72 w-[42rem] -translate-x-1/2 rounded-full bg-brand-radial blur-2xl" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left content */}
          <div className="text-center md:text-left animate-fade-up">
            <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 mb-6">
              <Shield className="w-4 h-4" />
              Research prototype - not for clinical use
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 leading-[1.1] mb-6">
              AI-assisted medical research.{' '}
              <span className="text-gradient">Honest by design.</span>
            </h1>
            
            <p className="text-lg text-slate-600 mb-8 leading-relaxed max-w-lg mx-auto md:mx-0">
              HomzDoctor is an open research workspace for AI-assisted medical record and imaging analysis. It provides no diagnosis, prescriptions, or medical advice, and its AI assistants stay off until their models are validated.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start mb-8">
              <Link
                to="/register"
                className="rounded-xl bg-brand-gradient px-6 py-3 text-center font-medium text-white shadow-soft transition-all hover:shadow-glow hover:brightness-[1.03]"
              >
                Explore the research →
              </Link>
              <Link
                to="#how-it-works"
                className="rounded-xl border border-slate-300 bg-white px-6 py-3 text-center font-medium text-slate-700 transition-colors hover:border-slate-400 hover:bg-slate-50"
              >
                See how it works
              </Link>
            </div>
            
            <div className="flex items-center gap-4 justify-center md:justify-start text-sm text-slate-500">
              <div className="flex items-center gap-1">
                <Microscope className="w-4 h-4" />
                <span>Research use only</span>
              </div>
              <div className="w-1 h-1 bg-slate-300 rounded-full" />
              <div className="flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                <span>Encrypted in transit</span>
              </div>
            </div>
          </div>
          
          {/* Right: product UI mockup (no image asset required) */}
          <div className="relative mt-12 md:mt-0 animate-fade-up [animation-delay:120ms]">
            {/* Main AI analysis card */}
            <div className="relative z-10 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-elevated">
              {/* Card header */}
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="rounded-lg bg-teal-600 p-1.5">
                    <Brain className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">AI Analysis</p>
                    <p className="text-xs text-slate-400">Integration pending</p>
                  </div>
                </div>
                <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500">
                  Disabled
                </span>
              </div>

              {/* Disabled state placeholder */}
              <div className="relative mb-4 flex h-40 flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 text-center">
                <Brain className="h-6 w-6 text-slate-400" />
                <p className="text-sm font-medium text-slate-600">No model connected</p>
                <p className="text-xs text-slate-500">
                  AI findings appear here only after a validated model endpoint is configured.
                </p>
              </div>

              {/* What works today */}
              <div className="space-y-2 text-xs text-slate-500">
                <p className="font-semibold text-slate-700">Working today</p>
                <p>Accounts, medical records, and file uploads.</p>
                <p className="pt-1 font-semibold text-slate-700">Not yet</p>
                <p>AI findings, confidence scores, and chat assistants.</p>
              </div>

              {/* Doctor review footer */}
              <div className="mt-4 flex items-center gap-3 rounded-lg border border-teal-100 bg-teal-50/60 p-3">
                <div className="text-xs">
                  <p className="font-semibold text-slate-900">No AI output is shown as medical fact</p>
                  <p className="text-slate-500">Nothing here is reviewed by a doctor</p>
                </div>
                <ShieldCheck className="ml-auto h-5 w-5 text-teal-600" />
              </div>
            </div>

            {/* Floating stat card */}
            <div className="absolute -bottom-5 -left-5 z-20 hidden animate-float items-center gap-2 rounded-xl border border-slate-200 bg-white p-3 shadow-elevated sm:flex">
              <div className="rounded-lg bg-emerald-50 p-1.5">
                <Activity className="h-4 w-4 text-emerald-600" />
              </div>
              <div className="text-xs">
                <p className="font-semibold text-slate-900">AI assistants</p>
                <p className="text-slate-500">in training</p>
              </div>
            </div>

            {/* Decorative glows */}
            <div className="absolute -right-6 -top-6 -z-10 h-28 w-28 rounded-full bg-teal-200 opacity-30 blur-3xl" />
            <div className="absolute -bottom-8 left-10 -z-10 h-24 w-24 rounded-full bg-emerald-200 opacity-30 blur-3xl" />
          </div>
        </div>
      </div>
      
      {/* Subtle wave separator */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent" />
    </section>
  );
}