import {
  Brain,
  Stethoscope,
  FileText,
  MessageCircle,
  Pill,
  MapPin,
  Calendar,
  AlertTriangle,
} from 'lucide-react';

export default function Features() {
  const features = [
    {
      icon: Brain,
      title: 'AI Analysis (research)',
      desc: 'Experimental analysis of X-rays, DICOM scans, and lab reports. Accuracy is unvalidated.',
      color: 'teal',
    },
    {
      icon: Stethoscope,
      title: 'Your Review',
      desc: 'Every AI finding is a research signal you inspect yourself; nothing is doctor-approved.',
      color: 'emerald',
    },
    {
      icon: FileText,
      title: 'Medical Records',
      desc: 'Securely upload and track imaging, DICOM files, and reports in one place.',
      color: 'teal',
    },
    {
      icon: MessageCircle,
      title: 'Patient Assistant (in training)',
      desc: 'AI chat stays disabled until its model finishes training and evaluation.',
      color: 'emerald',
    },
    {
      icon: Pill,
      title: 'Medication Tracking',
      desc: 'Log medications and reminders. No prescriptions are issued anywhere in this app.',
      color: 'teal',
    },
    {
      icon: MapPin,
      title: 'Pharmacy Finder',
      desc: 'Locate nearby pharmacies, check inventory, and place orders directly.',
      color: 'emerald',
    },
    {
      icon: Calendar,
      title: 'Appointments (planned)',
      desc: 'Scheduling is a roadmap item, not a live feature.',
      color: 'teal',
    },
    {
      icon: AlertTriangle,
      title: 'Safety Escalation (planned)',
      desc: 'No live monitoring exists here. In an emergency, call your local emergency number.',
      color: 'emerald',
    },
  ];

  const groupedFeatures = [
    { category: 'Diagnose & Analyze', items: features.slice(0, 2) },
    { category: 'Manage Your Care', items: features.slice(2, 4) },
    { category: 'Treatment & Support', items: features.slice(4, 6) },
    { category: 'Safety & Coordination', items: features.slice(6, 8) },
  ];

  return (
    <section id="features" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Complete clinical toolkit for home care
          </h2>
          <p className="text-lg text-slate-600">
            Everything you need to manage health at home, backed by physician oversight.
          </p>
        </div>

        <div className="space-y-16">
          {groupedFeatures.map((group) => (
            <div key={group.category}>
              <h3 className="text-xl font-semibold text-slate-800 mb-6 text-center md:text-left">
                {group.category}
              </h3>
              <div className="grid md:grid-cols-2 gap-6">
                {group.items.map((feature) => (
                  <div
                    key={feature.title}
                    className="group p-6 rounded-xl border border-slate-200 hover:border-teal-200 hover:shadow-md transition-all bg-white"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <feature.icon className="w-8 h-8 text-teal-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-900 mb-2">{feature.title}</h4>
                        <p className="text-slate-600 leading-relaxed">{feature.desc}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}