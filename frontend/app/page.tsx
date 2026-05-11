import Link from "next/link";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <>
      <header className="fixed top-0 left-0 w-full z-50 bg-surface border-b border-outline-variant shadow-sm h-16">
        <nav className="max-w-[1280px] mx-auto px-8 h-full flex justify-between items-center">
          <div className="flex items-center gap-8">
            <span className="text-xl font-black text-primary tracking-tight">PropViz AI</span>
            <div className="hidden md:flex items-center gap-6 text-sm font-medium">
              <Link href="/upload" className="text-on-surface-variant hover:text-primary transition-colors">New Tour</Link>
              <Link href="/dashboard" className="text-on-surface-variant hover:text-primary transition-colors">Dashboard</Link>
            </div>
          </div>
          <Link href="/login" className="text-sm font-bold text-primary hover:underline">Login</Link>
        </nav>
      </header>

      <main className="pt-16 flex-grow">
        {/* Hero */}
        <section className="relative min-h-[870px] flex flex-col items-center justify-center text-center px-6 overflow-hidden bg-surface-bright">
          <div className="absolute inset-0 z-0 opacity-10 pointer-events-none">
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-container rounded-full blur-[120px]" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-tertiary-container rounded-full blur-[120px]" />
          </div>
          <div className="relative z-10 max-w-4xl mx-auto space-y-8">
            <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-secondary-container/30 border border-secondary/20 text-secondary font-medium text-sm">
              <span className="material-symbols-outlined text-sm mr-2">auto_awesome</span>
              Introducing Automated Video Tours
            </div>
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-on-background leading-tight">
              Turn Floor Plans Into <br />
              <span className="text-primary-container drop-shadow-sm">Immersive Tours</span>
            </h1>
            <p className="text-xl md:text-2xl text-on-surface-variant max-w-2xl mx-auto leading-relaxed font-light">
              Upload a floor plan and brochure — PropViz AI generates a 90-second video tour your buyers can watch from home.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link href="/upload" className="px-8 py-4 bg-primary-container text-on-primary text-lg font-bold rounded-xl shadow-lg hover:shadow-xl transform transition-all active:scale-95 flex items-center gap-2">
                Create First Tour
                <span className="material-symbols-outlined">arrow_forward</span>
              </Link>
              <Link href="/dashboard" className="px-8 py-4 bg-surface-container-lowest border border-outline-variant text-on-surface text-lg font-semibold rounded-xl hover:bg-surface-container transition-colors shadow-sm active:scale-95">
                View Dashboard
              </Link>
            </div>
          </div>
        </section>

        {/* Feature Bento */}
        <section className="py-24 px-8 max-w-[1280px] mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            <div className="md:col-span-8 bg-surface-container-lowest p-8 md:p-12 rounded-[2rem] shadow-sm border border-outline-variant/30 flex flex-col justify-between group hover:shadow-md transition-shadow">
              <div>
                <div className="w-12 h-12 rounded-xl bg-primary-container/20 flex items-center justify-center mb-6">
                  <span className="material-symbols-outlined text-primary">architecture</span>
                </div>
                <h3 className="text-3xl font-bold mb-4">Precision Analysis</h3>
                <p className="text-on-surface-variant text-lg leading-relaxed max-w-md">
                  Our AI interprets architectural drawings with surgical precision, mapping spatial flow and light paths automatically.
                </p>
              </div>
              <div className="mt-12 flex items-center gap-4 text-primary font-bold">
                <span>Explore our technology</span>
                <span className="material-symbols-outlined transition-transform group-hover:translate-x-1">trending_flat</span>
              </div>
            </div>
            <div className="md:col-span-4 bg-primary text-on-primary p-8 rounded-[2rem] shadow-lg flex flex-col items-center text-center justify-center relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-20">
                <span className="material-symbols-outlined text-8xl">speed</span>
              </div>
              <h3 className="text-6xl font-black mb-2">90s</h3>
              <p className="text-primary-fixed text-lg font-medium">Generation Speed</p>
              <div className="mt-8 px-6 py-2 bg-on-primary text-primary rounded-full font-bold text-sm">Lightning Fast</div>
            </div>
            <div className="md:col-span-4 bg-surface-container-high p-8 rounded-[2rem] shadow-sm border border-outline-variant/30">
              <span className="material-symbols-outlined text-3xl text-secondary mb-4 block">share</span>
              <h3 className="text-xl font-bold mb-2">Instant Sharing</h3>
              <p className="text-on-surface-variant">Export directly to social platforms or share with buyers via WhatsApp link.</p>
            </div>
            <div className="md:col-span-8 bg-surface p-8 rounded-[2rem] shadow-sm border border-outline-variant/30 flex items-center gap-8">
              <div className="hidden lg:block w-32 h-32 rounded-2xl bg-gradient-to-br from-primary-container to-secondary-container flex-shrink-0" />
              <div>
                <h3 className="text-2xl font-bold mb-2">Branded for You</h3>
                <p className="text-on-surface-variant text-lg">Every tour is automatically themed with your agency&apos;s brand and agent contact details.</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-24 bg-on-background text-white overflow-hidden relative">
          <div className="max-w-[1280px] mx-auto px-8 flex flex-col lg:flex-row items-center gap-16">
            <div className="lg:w-1/2">
              <h2 className="text-4xl md:text-5xl font-bold leading-tight mb-8">Ready to transform your listings into interactive experiences?</h2>
              <div className="flex flex-col gap-4">
                <div className="flex items-start gap-4">
                  <span className="material-symbols-outlined text-primary-container" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>
                  <div>
                    <p className="font-bold text-lg">No hardware required</p>
                    <p className="text-outline-variant">Work entirely from existing digital assets.</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <span className="material-symbols-outlined text-primary-container" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>
                  <div>
                    <p className="font-bold text-lg">Works with off-plan properties</p>
                    <p className="text-outline-variant">Generate tours before construction is complete.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="lg:w-1/2 w-full">
              <div className="bg-surface-container-lowest/10 p-1 rounded-3xl backdrop-blur-sm border border-white/10">
                <div className="bg-surface p-8 rounded-2xl text-on-surface">
                  <h4 className="text-2xl font-bold mb-6 text-center">Start Generating Now</h4>
                  <div className="space-y-4">
                    <Link href="/upload" className="flex flex-col items-center justify-center gap-3 p-8 border-2 border-dashed border-outline-variant rounded-xl bg-surface-container-low hover:bg-surface-container-high transition-colors cursor-pointer group">
                      <span className="material-symbols-outlined text-4xl text-outline group-hover:text-primary transition-colors">upload_file</span>
                      <p className="text-sm font-medium text-on-surface-variant">Drop PDF or JPG floor plans here</p>
                    </Link>
                    <Link href="/upload" className="block w-full py-4 bg-primary text-on-primary font-bold rounded-xl text-center active:scale-95 transition-all shadow-lg">
                      Process Your First Tour
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
