import { Brain, CheckCircle, Shield, Users, FileCheck } from 'lucide-react';

export default function DoctorOversight() {
  const steps = [
    {
      icon: Brain,
      title: '1. AI analyzes your data',
      desc: 'Our algorithms review medical records, images, and symptoms.',
    },
    {
      icon: Users,
      title: '2. Doctor reviews findings',
      desc: 'Licensed physician examines every AI-generated insight.',
    },
    {
      icon: FileCheck,
      title: '3. Clinical decision',
      desc: 'Doctor approves, adjusts, or requests more information.',
    },
    {
      icon: CheckCircle,
      title: '4. You receive care',
      desc: 'Final diagnosis, prescription, or treatment plan delivered.',
    },
  ];

  return (
    <section className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left content */}
          <div>
            <div className="inline-flex items-center gap-2 bg-teal-100 text-teal-700 px-3 py-1 rounded-full text-sm font-medium mb-6">
              <Shield className="w-4 h-4" />
              Human-in-the-loop
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-6">
              AI assists. Doctors decide.
            </h2>
            <p className="text-lg text-slate-600 mb-8 leading-relaxed">
              Every medical finding, diagnosis suggestion, and prescription recommendation 
              goes through a licensed physician before reaching you. AI handles the heavy 
              lifting — doctors provide the clinical judgment.
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
                <span className="font-semibold text-teal-600">⭐ 100% doctor-reviewed</span>{' '}
                — No AI decision reaches you without a licensed physician's approval.
              </p>
            </div>
          </div>
          
          {/* Right image placeholder */}
          <div className="relative">
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
              <img
                src="/assets/doctor-reviewing-ai.jpg"
                alt="Licensed doctor reviewing AI analysis on tablet"
                className="w-full h-auto"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://placehold.co/600x500/e2e8f0/475569?text=Doctor+reviewing+AI+findings';
                }}
              />
              <div className="absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-sm p-3 rounded-lg border border-teal-200 shadow-sm">
                <p className="text-sm font-medium text-teal-800">
                  ✓ Reviewed by Dr. Sarah Chen, MD — Internal Medicine
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}