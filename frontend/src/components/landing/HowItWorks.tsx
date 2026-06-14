import { Upload, Brain, Stethoscope, CheckCircle } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      icon: Upload,
      title: 'Share your health data',
      desc: 'Upload medical records, describe symptoms, or ask the AI assistant.',
      color: 'bg-teal-100',
    },
    {
      icon: Brain,
      title: 'AI analyzes',
      desc: 'Advanced algorithms review your information against medical knowledge.',
      color: 'bg-emerald-100',
    },
    {
      icon: Stethoscope,
      title: 'Doctor reviews',
      desc: 'Licensed physician examines every finding and adds clinical judgment.',
      color: 'bg-teal-100',
    },
    {
      icon: CheckCircle,
      title: 'Get your care plan',
      desc: 'Receive diagnosis, prescription, or next steps — all doctor-approved.',
      color: 'bg-emerald-100',
    },
  ];

  return (
    <section id="how-it-works" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            How HomzDoctor works
          </h2>
          <p className="text-lg text-slate-600">
            Four simple steps from symptom to care — with physician oversight at every stage.
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-8 relative">
          {/* Connecting line (desktop) */}
          <div className="hidden md:block absolute top-1/3 left-0 right-0 h-0.5 bg-slate-200 -z-10" />
          
          {steps.map((step, idx) => (
            <div key={step.title} className="relative text-center">
              <div className={`${step.color} w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm`}>
                <step.icon className="w-8 h-8 text-teal-700" />
              </div>
              <div className="text-sm font-semibold text-teal-600 mb-2">Step {idx + 1}</div>
              <h3 className="font-semibold text-slate-900 mb-2">{step.title}</h3>
              <p className="text-sm text-slate-600">{step.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-sm text-slate-500 max-w-2xl mx-auto">
            ⚠️ Not for emergencies. If you're experiencing a medical emergency, 
            call your local emergency number immediately.
          </p>
        </div>
      </div>
    </section>
  );
}