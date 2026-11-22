import { Stethoscope, Github } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          {/* Brand column */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="bg-teal-600 p-1.5 rounded-lg">
                <Stethoscope className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-semibold text-white">
                Homz<span className="text-teal-400">Doctor</span>
              </span>
            </div>
            <p className="text-sm text-slate-400">
              An open research workspace for medical AI - no diagnosis, no prescriptions, no clinical claims.
            </p>
          </div>

          {/* Product links */}
          <div>
            <h3 className="font-semibold text-white mb-3">Product</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#features" className="hover:text-teal-400 transition-colors">Features</a></li>
              <li><a href="#how-it-works" className="hover:text-teal-400 transition-colors">How it works</a></li>
              <li><a href="#security" className="hover:text-teal-400 transition-colors">Security</a></li>
            </ul>
          </div>

        </div>

        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-slate-400">
            © 2024 HomzDoctor. All rights reserved. Not for emergencies.
          </div>
          <div className="flex gap-4">
            <a href="https://github.com/minagayid/homzdoctor" className="text-slate-400 hover:text-teal-400 transition-colors">
              <Github className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}