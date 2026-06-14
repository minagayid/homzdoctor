import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs = [
    {
      q: 'Is HomzDoctor a replacement for my primary care doctor?',
      a: 'No. HomzDoctor is a complementary tool that works alongside your existing healthcare providers. We provide AI-assisted analysis with doctor oversight, but we don\'t replace your primary care relationship or emergency services.',
    },
    {
      q: 'Who reviews the AI findings?',
      a: 'Every AI-generated finding, diagnosis suggestion, and prescription recommendation is reviewed by a licensed US-based physician before you see it. You\'ll always know a real doctor has approved your care plan.',
    },
    {
      q: 'Is my medical data secure and private?',
      a: 'Absolutely. We\'re fully HIPAA compliant, use end-to-end encryption, and never sell your data. You maintain full ownership and control over your medical information.',
    },
    {
      q: 'What can the AI analyze?',
      a: 'Our AI can analyze medical images (X-rays, DICOM scans, MRIs), lab reports, symptoms, medical history, and medication interactions. All findings are reviewed by a doctor before delivery.',
    },
    {
      q: 'How much does HomzDoctor cost?',
      a: 'We offer flexible plans starting at $19/month for basic AI chat and record storage. Full clinical features including doctor-reviewed diagnostics start at $49/month. Insurance partnerships coming soon.',
    },
    {
      q: 'Can my doctor use HomzDoctor too?',
      a: 'Yes! We have a provider portal where your existing doctor can access shared records and see our AI analysis. Many physicians are joining our network to enhance their practice.',
    },
    {
      q: 'What happens if the AI detects something serious?',
      a: 'Our safety escalation system immediately flags concerning findings for priority doctor review. The physician will contact you directly and may recommend immediate in-person care.',
    },
  ];

  return (
    <section id="faq" className="py-24 bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Questions? We have answers.
          </h2>
          <p className="text-lg text-slate-600">
            Everything you need to know about AI-powered, doctor-reviewed care.
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <div key={idx} className="border border-slate-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setOpenIndex(openIndex === idx ? null : idx)}
                className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-slate-50 transition-colors"
                aria-expanded={openIndex === idx}
              >
                <span className="font-medium text-slate-900">{faq.q}</span>
                <ChevronDown
                  className={`w-5 h-5 text-slate-500 transition-transform ${
                    openIndex === idx ? 'rotate-180' : ''
                  }`}
                />
              </button>
              <div
                className={`px-6 overflow-hidden transition-all duration-200 ${
                  openIndex === idx ? 'py-4 border-t border-slate-200' : 'max-h-0 py-0'
                }`}
              >
                <p className="text-slate-600">{faq.a}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}