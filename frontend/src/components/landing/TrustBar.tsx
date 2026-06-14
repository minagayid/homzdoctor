export default function TrustBar() {
  const trustItems = [
    { label: 'HIPAA Aligned', desc: 'Enterprise security' },
    { label: 'Doctor-Reviewed', desc: 'Human oversight' },
    { label: 'End-to-end Encrypted', desc: 'Your data private' },
    { label: 'Licensed Physicians', desc: 'US-based network' },
  ];

  return (
    <section className="py-12 bg-slate-50 border-y border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-sm font-medium text-slate-500 uppercase tracking-wide mb-8">
          Trusted infrastructure for clinical care
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {trustItems.map((item) => (
            <div key={item.label} className="text-center">
              <div className="text-teal-600 font-bold text-lg mb-1">{item.label}</div>
              <div className="text-sm text-slate-500">{item.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}