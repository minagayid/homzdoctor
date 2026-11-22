import { CheckCircle, Shield, Users, FileCheck } from 'lucide-react';

export default function DoctorOversight() {
  const steps = [
    {
      icon: Users,
      title: '1. You review findings',
      desc: 'Every AI-generated insight is unvalidated and shown for your own review.',
    },
    {
      icon: FileCheck,
      title: '2. No clinical decisions',
      desc: 'The platform makes no diagnoses, prescriptions, or treatment plans.',
    },
    {
      icon: CheckCircle,
      title: '3. Real care stays with clinicians',
      desc: 'Take anything that matters to a qualified, licensed clinician.',
    },
  ];

  return (
    <section className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl">
          {/* Left content */}
          <div>
            <div className="inline-flex items-center gap-2 bg-teal-100 text-teal-700 px-3 py-1 rounded-full text-sm font-medium mb-6">
              <Shield className="w-4 h-4" />
              Human-in-the-loop
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-6">
              AI proposes nothing yet. You decide.
            </h2>
            <p className="text-lg text-slate-600 mb-8 leading-relaxed">
              Every AI output here is an unvalidated research signal shown for your own
              inspection. Nothing is reviewed by a physician, and any real health decision
              belongs with a qualified, licensed clinician.
            </p>
            
            <div className="space-y-4 mb-8">
              {steps.map((step) => (
                <div key={step.title} className="flex gap-3">
                  <step.icon className="w-6 h-6 text-teal-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-slate-900">{step.title}</h3>
                    <p className="text-slate-600 text-sm">{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
              <p className="text-sm text-slate-600">
                <span className="font-semibold text-teal-600">No clinical review occurs here</span>{' '}
                — AI assistants stay disabled until their models are validated.
              </p>
            </div>
          </div>
          
        </div>
      </div>
    </section>
  );
}