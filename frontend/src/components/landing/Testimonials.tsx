import { Star } from 'lucide-react';

export default function Testimonials() {
  const testimonials = [
    {
      name: 'Michael Torres',
      role: 'Patient, Father of two',
      content: 'Having a doctor review the AI findings before I saw them gave me real peace of mind. HomzDoctor caught something my previous doctor missed.',
      avatar: '/assets/avatar-patient-1.jpg',
      rating: 5,
    },
    {
      name: 'Dr. Sarah Chen, MD',
      role: 'Internal Medicine, HomzDoctor Medical Network',
      content: 'The AI saves me hours of documentation time, but I still make every final call. It\'s the perfect balance of efficiency and clinical safety.',
      avatar: '/assets/avatar-doctor-1.jpg',
      rating: 5,
    },
    {
      name: 'Elena Rodriguez',
      role: 'Chronic care patient',
      content: 'My medication adherence has improved dramatically with the reminders and pharmacist integration. And knowing a real doctor oversees everything? Game changer.',
      avatar: '/assets/avatar-patient-2.jpg',
      rating: 5,
    },
  ];

  return (
    <section className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Trusted by patients and physicians
          </h2>
          <p className="text-lg text-slate-600">
            Real experiences from people who've made HomzDoctor part of their health journey.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div key={testimonial.name} className="bg-slate-50 p-6 rounded-xl border border-slate-200">
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-teal-600 text-teal-600" />
                ))}
              </div>
              <p className="text-slate-700 mb-6 leading-relaxed">"{testimonial.content}"</p>
              <div className="flex items-center gap-3">
                <img
                  src={testimonial.avatar}
                  alt={testimonial.name}
                  className="w-10 h-10 rounded-full object-cover bg-slate-200"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://placehold.co/40x40/e2e8f0/475569?text=👤';
                  }}
                />
                <div>
                  <div className="font-semibold text-slate-900">{testimonial.name}</div>
                  <div className="text-sm text-slate-500">{testimonial.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}