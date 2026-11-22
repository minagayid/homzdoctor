import {
  Brain,
  Stethoscope,
  FileText,
  MessageCircle,
  Pill,
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

  return (
    <section id="features" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature) => (
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
    </section>
  );
}