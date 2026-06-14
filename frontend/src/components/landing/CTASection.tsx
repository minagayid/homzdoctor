import { Link } from 'react-router-dom';
import { ArrowRight, Shield, Clock } from 'lucide-react';

export default function CTASection() {
  return (
    <section className="py-24 bg-gradient-to-br from-teal-600 to-teal-700">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
          Ready for doctor-reviewed AI care?
        </h2>
        <p className="text-lg text-teal-100 mb-8">
          Join thousands of patients getting clinical-grade insights from home.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <Link
            to="/register"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-teal-600 rounded-lg font-semibold hover:bg-slate-50 transition-colors shadow-md"
          >
            Start your free assessment
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="#how-it-works"
            className="inline-flex items-center gap-2 px-6 py-3 border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10 transition-colors"
          >
            See the platform
          </Link>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-6 justify-center text-sm text-teal-100">
          <div className="flex items-center gap-2 justify-center">
            <Shield className="w-4 h-4" />
            <span>Doctor-reviewed</span>
          </div>
          <div className="flex items-center gap-2 justify-center">
            <Clock className="w-4 h-4" />
            <span>No commitment, cancel anytime</span>
          </div>
        </div>
      </div>
    </section>
  );
}