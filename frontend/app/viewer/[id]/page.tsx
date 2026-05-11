"use client";
import { use } from "react";
import { useJob } from "@/hooks/useJob";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

const STAGE_LABELS: Record<string, string> = {
  ingest:          "Validating files",
  parse:           "Extracting floor plan & specs",
  reconstruct:     "Generating interior renders",
  synthesize:      "Creating narration audio",
  postprocess:     "Assembling final video",
};

export default function ViewerPage({ params }: { params: Promise<{ id: string }> }) {
  const { id: jobId } = use(params);
  const { job, error } = useJob(jobId);

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="pt-24 pb-16 max-w-[1280px] mx-auto px-8 flex-grow w-full">
        {error && <p className="text-error text-center py-8">{error}</p>}

        {!job && !error && (
          <div className="flex items-center justify-center h-64">
            <div className="w-10 h-10 border-4 border-primary-container border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {job && job.status === "complete" && job.output_url && (
          <>
            {/* Video player */}
            <section className="w-full mb-12">
              <div className="relative aspect-video w-full rounded-xl overflow-hidden bg-on-background shadow-2xl">
                <video
                  src={job.output_url}
                  className="w-full h-full object-cover"
                  controls
                  playsInline
                />
              </div>
            </section>

            {/* Content grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 items-start">
              <div className="lg:col-span-2 space-y-6">
                <div>
                  <h1 className="text-4xl md:text-5xl font-black text-on-background tracking-tight mb-2">
                    Property Virtual Tour
                  </h1>
                  <div className="flex items-center gap-2 text-on-surface-variant font-medium">
                    <span className="material-symbols-outlined text-primary">location_on</span>
                    <span className="text-xl">Aftabnagar, Dhaka</span>
                  </div>
                </div>

                {/* Asset list */}
                {job.assets.length > 0 && (
                  <div className="space-y-2 pt-4 border-t border-outline-variant">
                    <h3 className="text-sm font-bold text-on-surface-variant uppercase tracking-wider">Generated Assets</h3>
                    <ul className="space-y-1">
                      {job.assets.map((a) => (
                        <li key={a.id} className="text-xs text-on-surface-variant flex justify-between">
                          <span>{a.original_filename}</span>
                          <span className="text-outline">{a.asset_type}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Interaction card */}
              <aside className="space-y-6">
                <div className="bg-surface-container-lowest p-8 rounded-xl shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] border border-outline-variant sticky top-24">
                  <h3 className="text-2xl font-bold text-on-background mb-4">Ready to see it in person?</h3>
                  <p className="text-on-surface-variant mb-8 leading-relaxed">
                    You&apos;ve seen the space virtually. Book a site visit and confirm with your own eyes.
                  </p>
                  <div className="space-y-4">
                    <a
                      href="https://wa.me/8801332560056?text=I+watched+the+virtual+tour+and+I%27d+like+to+visit+the+property."
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-3 w-full bg-secondary text-on-secondary py-4 px-6 rounded-lg font-bold transition-transform active:scale-95 hover:brightness-110"
                    >
                      <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>chat</span>
                      Book Site Visit
                    </a>
                    <button
                      onClick={copyLink}
                      className="flex items-center justify-center gap-3 w-full border border-outline-variant text-on-surface py-4 px-6 rounded-lg font-bold transition-all hover:bg-surface-container-low active:scale-95"
                    >
                      <span className="material-symbols-outlined">share</span>
                      Share this tour
                    </button>
                  </div>

                  <div className="mt-8 pt-6 border-t border-outline-variant">
                    <div className="flex items-start gap-3">
                      <span className="material-symbols-outlined text-primary">verified</span>
                      <div>
                        <h4 className="font-bold text-primary mb-1">PropViz Certified</h4>
                        <p className="text-xs text-on-surface-variant">This tour has been AI-verified for spatial accuracy.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </aside>
            </div>
          </>
        )}

        {/* Processing state */}
        {job && job.status !== "complete" && (
          <div className="max-w-2xl mx-auto bg-surface-container-lowest rounded-xl shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] p-12 border border-outline-variant flex flex-col items-center text-center mt-8">
            <div className="mb-8">
              <div className="w-20 h-20 bg-surface-container-low rounded-full flex items-center justify-center text-primary-container mb-4 mx-auto">
                <span className="material-symbols-outlined text-4xl" style={{fontVariationSettings: "'FILL' 1"}}>architecture</span>
              </div>
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${job.status === "failed" ? "bg-error/10 border border-error/20 text-error" : "bg-tertiary-container/10 border border-tertiary-container/20 text-tertiary"}`}>
                <span className={`w-2 h-2 rounded-full mr-2 ${job.status === "failed" ? "bg-error" : "bg-tertiary"}`} />
                {job.status}
              </div>
            </div>

            <h1 className="text-3xl font-black text-on-surface tracking-tight mb-2">
              {job.status === "failed" ? "Generation failed" : "Generating your tour"}
            </h1>
            <p className="text-on-surface-variant max-w-sm mb-8">
              {job.status === "failed"
                ? job.error_message
                : (job.current_stage ? STAGE_LABELS[job.current_stage] ?? job.current_stage : "Processing your files…")}
            </p>

            <div className="mb-4">
              <span className="text-6xl font-black text-primary tracking-tighter">{job.progress_pct}%</span>
            </div>
            <div className="w-full max-w-md bg-surface-container-high h-4 rounded-full overflow-hidden mb-8 p-1">
              <div
                className="h-full bg-primary-container rounded-full progress-bar-glow transition-all duration-500"
                style={{ width: `${job.progress_pct}%` }}
              />
            </div>
            {job.status !== "failed" && (
              <p className="text-xs text-on-surface-variant italic">Please do not close this window while processing is active.</p>
            )}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
