import { useState } from 'react';
import { Users, Briefcase, Clock, BarChart3 as ChartBar, Calendar, Shield as ShieldIcon } from 'lucide-react';

export default function ForPatientsDoctors() {
  const [activeTab, setActiveTab] = useState<'patients' | 'doctors'>('patients');

  const patientBenefits = [
    { icon: Clock, title: '24/7 access', desc: 'Get answers anytime, not just during office hours.' },
    { icon: ShieldIcon, title: 'Doctor-reviewed', desc: 'Every AI finding checked by a real physician.' },
    { icon: Calendar, title: 'Faster care', desc: 'Reduce wait times from weeks to hours.' },
    { icon: ChartBar, title: 'Track everything', desc: 'All records, prescriptions, and scans in one place.' },
  ];

  const doctorBenefits = [
    { icon: Briefcase, title: 'Reduce workload', desc: 'AI handles initial analysis and documentation.' },
    { icon: Clock, title: 'Focus on complex cases', desc: 'Spend time where clinical judgment matters most.' },
    { icon: ChartBar, title: 'Clinical insights', desc: 'AI highlights patterns you might miss.' },
    { icon: ShieldIcon, title: 'Better outcomes', desc: 'Catch issues earlier with continuous monitoring.' },
  ];

  return (
    <section id="for-doctors" className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Built for patients and doctors
          </h2>
          <p className="text-lg text-slate-600">
            One platform that serves everyone in the care journey.
          </p>
        </div>

        {/* Tab buttons */}
        <div className="flex justify-center gap-4 mb-12">
          <button
            onClick={() => setActiveTab('patients')}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              activeTab === 'patients'
                ? 'bg-teal-600 text-white shadow-sm'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <Users className="w-4 h-4 inline mr-2" />
            For Patients
          </button>
          <button
            onClick={() => setActiveTab('doctors')}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              activeTab === 'doctors'
                ? 'bg-teal-600 text-white shadow-sm'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <Briefcase className="w-4 h-4 inline mr-2" />
            For Doctors
          </button>
        </div>

        {/* Content panels */}
        <div className="max-w-4xl mx-auto">
          {activeTab === 'patients' && (
            <div className="grid md:grid-cols-2 gap-6 fade-in-visible">
              {patientBenefits.map((benefit) => (
                <div key={benefit.title} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <benefit.icon className="w-8 h-8 text-teal-600 mb-3" />
                  <h3 className="font-semibold text-slate-900 mb-2">{benefit.title}</h3>
                  <p className="text-slate-600">{benefit.desc}</p>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'doctors' && (
            <div className="grid md:grid-cols-2 gap-6 fade-in-visible">
              {doctorBenefits.map((benefit) => (
                <div key={benefit.title} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <benefit.icon className="w-8 h-8 text-teal-600 mb-3" />
                  <h3 className="font-semibold text-slate-900 mb-2">{benefit.title}</h3>
                  <p className="text-slate-600">{benefit.desc}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-slate-500">
            <span className="font-semibold text-teal-600">For physicians:</span> Join our medical network —{' '}
            <a href="#" className="text-teal-600 underline">learn about partnership opportunities</a>
          </p>
        </div>
      </div>
    </section>
  );
}