import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs = [
    {
      q: 'Is HomzDoctor a replacement for my primary care doctor?',
      a: 'No. HomzDoctor is a research prototype for exploring medical AI. It is not a medical service, gives no medical advice, and must never replace your doctors or emergency services.',
    },
    {
      q: 'Who reviews the AI findings?',
      a: 'No one. AI outputs are unvalidated research signals shown for experimentation only. Always consult a qualified physician for any health decision.',
    },
    {
      q: 'Is my medical data secure and private?',
      a: 'Connections are encrypted in transit and uploads live in a private per-user database, but this research project has not been audited for HIPAA or any other regulation. Do not upload real patient data.',
    },
    {
      q: 'What can the AI analyze?',
      a: 'The goal is analysis of medical images (X-rays, DICOM), lab reports, and symptoms. The AI assistants remain off until their models finish training and evaluation.',
    },
    {
      q: 'How much does HomzDoctor cost?',
      a: 'Nothing. This is a free research prototype. There are no paid plans, no insurance partnerships, and no clinical services.',
    },
    {
      q: 'Can my doctor use HomzDoctor too?',
      a: 'There is no provider portal or physician network. This is a personal research workspace; share exports with your own doctor if you choose.',
    },
    {
      q: 'What happens if the AI detects something serious?',
      a: 'There is no live monitoring or escalation. If you have concerning symptoms, contact a doctor or emergency services directly.',
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