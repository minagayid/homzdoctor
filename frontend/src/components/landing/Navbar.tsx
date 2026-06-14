import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, Stethoscope, LogIn, UserPlus } from 'lucide-react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const navLinks = [
    { name: 'Features', href: '#features' },
    { name: 'How it works', href: '#how-it-works' },
    { name: 'For Doctors', href: '#for-doctors' },
    { name: 'Security', href: '#security' },
    { name: 'FAQ', href: '#faq' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="bg-teal-600 p-1.5 rounded-lg">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-slate-900">
              Homz<span className="text-teal-600">Doctor</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-slate-600 hover:text-teal-600 transition-colors text-sm font-medium"
              >
                {link.name}
              </a>
            ))}
          </div>

          {/* Desktop buttons */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              to="/login"
              className="px-4 py-2 text-slate-700 hover:text-slate-900 text-sm font-medium transition-colors flex items-center gap-2"
            >
              <LogIn className="w-4 h-4" />
              Log in
            </Link>
            <Link
              to="/register"
              className="px-5 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors text-sm font-medium flex items-center gap-2 shadow-sm"
            >
              <UserPlus className="w-4 h-4" />
              Get started
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-slate-100 transition-colors"
            aria-label="Toggle menu"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="md:hidden py-4 border-t border-slate-200">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className="block py-3 text-slate-600 hover:text-teal-600 transition-colors"
              >
                {link.name}
              </a>
            ))}
            <div className="pt-4 flex gap-3">
              <Link
                to="/login"
                className="flex-1 px-4 py-2 border border-slate-300 text-center rounded-lg text-slate-700 hover:bg-slate-50 transition-colors"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="flex-1 px-4 py-2 bg-teal-600 text-center text-white rounded-lg hover:bg-teal-700 transition-colors"
              >
                Get started
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}