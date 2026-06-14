import { Shield, Lock, Database, Eye, FileText, UserCheck } from 'lucide-react';

export default function SecurityCompliance() {
  const securityItems = [
    {
      icon: Shield,
      title: 'HIPAA Compliant',
      desc: 'Enterprise-grade security meeting all regulatory requirements.',
    },
    {
      icon: Lock,
      title: 'End-to-end Encryption',
      desc: 'Your data is encrypted at rest and in transit.',
    },
    {
      icon: Database,
      title: 'Secure Storage',
      desc: 'Medical records stored in compliant, audited facilities.',
    },
    {
      icon: Eye,
      title: 'Access Controls',
      desc: 'You control who sees your medical information.',
    },
    {
      icon: FileText,
      title: 'Audit Trails',
      desc: 'Every access to your data is logged and reviewable.',
    },
    {
      icon: UserCheck,
      title: 'Doctor Oversight',
      desc: 'No AI decisions without licensed physician approval.',
    },
  ];

  return (
    <section id="security" className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Security & compliance you can trust
          </h2>
          <p className="text-lg text-slate-600">
            Your health data deserves the highest level of protection. We meet or exceed 
            all clinical and privacy standards.
          </p>
        </div>

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