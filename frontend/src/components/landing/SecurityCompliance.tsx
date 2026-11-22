import { Shield, Eye, UserCheck } from 'lucide-react';

export default function SecurityCompliance() {
  const securityItems = [
    {
      icon: Shield,
      title: 'Not compliance-audited',
      desc: 'A research project: no HIPAA or regulatory audit. Do not upload real patient data.',
    },
    {
      icon: Eye,
      title: 'Access Controls',
      desc: 'You control who sees your medical information.',
    },
    {
      icon: UserCheck,
      title: 'Human oversight',
      desc: 'AI outputs are research signals; any real decision needs a qualified clinician.',
    },
  ];

  return (
    <section id="security" className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {securityItems.map((item) => (
            <div key={item.title} className="bg-white p-6 rounded-xl border border-slate-200">
              <item.icon className="w-8 h-8 text-teal-600 mb-3" />
              <h3 className="font-semibold text-slate-900 mb-2">{item.title}</h3>
              <p className="text-sm text-slate-600">{item.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-xs text-slate-400">
            HomzDoctor is not a replacement for emergency medical care. In emergencies, call your local emergency number.
          </p>
        </div>
      </div>
    </section>
  );
}