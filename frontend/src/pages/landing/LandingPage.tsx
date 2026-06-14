import Navbar from '../../components/landing/Navbar';
import Hero from '../../components/landing/Hero';
import TrustBar from '../../components/landing/TrustBar';
import Features from '../../components/landing/Features';
import HowItWorks from '../../components/landing/HowItWorks';
import DoctorOversight from '../../components/landing/DoctorOversight';
import ForPatientsDoctors from '../../components/landing/ForPatientsDoctors';
import Testimonials from '../../components/landing/Testimonials';
import SecurityCompliance from '../../components/landing/SecurityCompliance';
import FAQ from '../../components/landing/FAQ';
import CTASection from '../../components/landing/CTASection';
import Footer from '../../components/landing/Footer';

/**
 * HomzDoctor public marketing landing page.
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <Navbar />
      <main>
        <Hero />
        <TrustBar />
        <Features />
        <DoctorOversight />
        <HowItWorks />
        <ForPatientsDoctors />
        <Testimonials />
        <SecurityCompliance />
        <FAQ />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
