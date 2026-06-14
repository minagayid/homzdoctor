import { Link } from 'react-router-dom';
import { Stethoscope, Twitter, Linkedin, Github, Mail } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
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
              AI-powered care with physician oversight — bringing clinical excellence home.
            </p>
          </div>

          {/* Product links */}
          <div>
            <h3 className="font-semibold text-white mb-3">Product</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#features" className="hover:text-teal-400 transition-colors">Features</a></li>
              <li><a href="#how-it-works" className="hover:text-teal-400 transition-colors">How it works</a></li>
              <li><a href="#security" className="hover:text-teal-400 transition-colors">Security</a></li>
              <li><Link to="/pricing" className="hover:text-teal-400 transition-colors">Pricing</Link></li>
            </ul>
          </div>

          {/* For Doctors */}
          <div>
            <h3 className="font-semibold text-white mb-3">For Doctors</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-teal-400 transition-colors">Join medical network</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">Provider portal</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">Clinical research</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">API for EHR</a></li>
            </ul>
          </div>

          {/* Legal & Company */}
          <div>
            <h3 className="font-semibold text-white mb-3">Company</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-teal-400 transition-colors">About us</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">Press</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">Contact</a></li>
              <li><a href="#" className="hover:text-teal-400 transition-colors">Privacy & Terms</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-slate-400">
            © 2024 HomzDoctor. All rights reserved. Not for emergencies.
          </div>
          <div className="flex gap-4">
            <a href="#" className="text-slate-400 hover:text-teal-400 transition-colors">
              <Twitter className="w-5 h-5" />
            </a>
            <a href="https://www.linkedin.com/in/haroon-sajid-ai/" className="text-slate-400 hover:text-teal-400 transition-colors">
              <Linkedin className="w-5 h-5" />
            </a>
            <a href="https://github.com/minagayid/homzdoctor" className="text-slate-400 hover:text-teal-400 transition-colors">
              <Github className="w-5 h-5" />
            </a>
            <a href="#" className="text-slate-400 hover:text-teal-400 transition-colors">
              <Mail className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}