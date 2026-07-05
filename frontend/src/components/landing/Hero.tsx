import { Link } from 'react-router-dom';
import { Shield, Microscope, Sparkles, Brain, CheckCircle2, ShieldCheck, Activity } from 'lucide-react';

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
              Reviewed by licensed doctors
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 leading-[1.1] mb-6">
              AI-powered care at home.{' '}
              <span className="text-gradient">Reviewed by real doctors.</span>
            </h1>
            
            <p className="text-lg text-slate-600 mb-8 leading-relaxed max-w-lg mx-auto md:mx-0">
              HomzDoctor combines advanced AI diagnostics with licensed physician oversight. 
              Get clinical-grade insights, prescriptions, and care coordination — all from home.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start mb-8">
              <Link
                to="/register"
                className="rounded-xl bg-brand-gradient px-6 py-3 text-center font-medium text-white shadow-soft transition-all hover:shadow-glow hover:brightness-[1.03]"
              >
                Start a symptom check →
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
                <span>AI + MD review</span>
              </div>
              <div className="w-1 h-1 bg-slate-300 rounded-full" />
              <div className="flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                <span>HIPAA compliant</span>
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
                    <p className="text-xs text-slate-400">Chest X-ray · just now</p>
                  </div>
                </div>
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">
                  <CheckCircle2 className="h-3.5 w-3.5" /> Complete
                </span>
              </div>

              {/* Scan preview with pulse line */}
              <div className="relative mb-4 h-40 overflow-hidden rounded-xl bg-slate-900">
                <svg
                  viewBox="0 0 300 160"
                  preserveAspectRatio="none"
                  className="absolute inset-0 h-full w-full"
                >
                  <defs>
                    <pattern id="heroGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                      <path d="M20 0 L0 0 0 20" fill="none" stroke="#1e293b" strokeWidth="1" />
                    </pattern>
                  </defs>
                  <rect width="300" height="160" fill="url(#heroGrid)" opacity="0.6" />
                  <polyline
                    points="0,100 45,100 65,45 85,125 105,100 150,100 170,60 190,108 235,100 270,100 285,70 300,100"
                    fill="none"
                    stroke="#2dd4bf"
                    strokeWidth="2.5"
                    strokeLinejoin="round"
                    strokeLinecap="round"
                  />
                </svg>
                {/* Sweeping analysis line */}
                <div className="absolute inset-x-0 top-0 h-8 animate-scan-sweep bg-gradient-to-b from-brand-400/40 to-transparent" />
                <span className="absolute left-2 top-2 font-mono text-[10px] text-brand-300/80">
                  SCAN_0481.dcm
                </span>
                <span className="absolute right-2 top-2 flex items-center gap-1 font-mono text-[10px] text-brand-300/80">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="absolute inline-flex h-full w-full animate-pulse-ring rounded-full bg-brand-400" />
                    <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-brand-400" />
                  </span>
                  ANALYZING
                </span>
              </div>

              {/* Finding + confidence */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-500">Finding</span>
                  <span className="text-sm font-medium text-slate-900">No acute abnormality</span>
                </div>
                <div>
                  <div className="mb-1 flex justify-between text-xs text-slate-500">
                    <span>Confidence</span>
                    <span>92%</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-slate-100">
                    <div className="h-2 w-[92%] rounded-full bg-teal-600" />
                  </div>
                </div>
              </div>

              {/* Doctor review footer */}
              <div className="mt-4 flex items-center gap-3 rounded-lg border border-teal-100 bg-teal-50/60 p-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-teal-600 text-xs font-semibold text-white">
                  SC
                </div>
                <div className="text-xs">
                  <p className="font-semibold text-slate-900">Reviewed by Dr. Sarah Chen, MD</p>
                  <p className="text-slate-500">Internal Medicine · Approved</p>
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
                <p className="font-semibold text-slate-900">Avg. doctor review</p>
                <p className="text-slate-500">under 2 hours</p>
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