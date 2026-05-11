"use client";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, PropertyInput } from "@/lib/api";
import { useJob } from "@/hooks/useJob";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

type Step = 1 | 2 | 3 | 4;
type AssetType = "floor_plan" | "brochure" | "photo";

interface UploadEntry { name: string; assetType: AssetType; progress: number; done: boolean; error?: string; }

const STAGE_LABELS: Record<string, string> = {
  ingest:      "Validating files",
  parse:       "Extracting floor plan & specs",
  reconstruct: "Generating interior renders",
  synthesize:  "Creating narration audio",
  postprocess: "Assembling final video",
};

const ACCEPT: Record<AssetType, string> = {
  floor_plan: "image/jpeg,image/png,image/webp,application/pdf",
  brochure:   "image/jpeg,image/png,image/webp,application/pdf",
  photo:      "image/jpeg,image/png,image/webp",
};

function StepIndicator({ step }: { step: Step }) {
  const steps = ["Property Details", "Upload Files", "Processing", "Done"];
  return (
    <div className="w-full max-w-3xl mx-auto mb-12">
      <div className="relative flex justify-between items-center">
        <div className="absolute top-5 left-0 w-full h-0.5 bg-outline-variant -z-10" />
        <div className="absolute top-5 left-0 h-0.5 bg-primary-container -z-10 transition-all duration-500" style={{ width: `${((step - 1) / 3) * 100}%` }} />
        {steps.map((label, i) => {
          const num = i + 1;
          const done = num < step;
          const active = num === step;
          return (
            <div key={i} className="flex flex-col items-center gap-2 relative z-10">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold shadow-sm transition-all ${done ? "bg-primary text-on-primary" : active ? "bg-primary-container text-on-primary-container ring-4 ring-primary-fixed" : "bg-surface-container-high text-on-surface-variant border border-outline-variant"}`}>
                {done
                  ? <span className="material-symbols-outlined text-sm" style={{fontVariationSettings: "'FILL' 1"}}>check</span>
                  : active && step === 4
                  ? <span className="material-symbols-outlined text-sm" style={{fontVariationSettings: "'FILL' 1"}}>celebration</span>
                  : num}
              </div>
              <span className={`text-xs font-medium hidden sm:block ${active ? "font-bold text-primary" : done ? "text-on-surface" : "text-on-surface-variant"}`}>{label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function UploadPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>(1);
  const [jobId, setJobId] = useState<string | null>(null);
  const [form, setForm] = useState<PropertyInput>({ name: "" });
  const [creating, setCreating] = useState(false);
  const [starting, setStarting] = useState(false);
  const [uploads, setUploads] = useState<UploadEntry[]>([]);
  const [activeTab, setActiveTab] = useState<AssetType>("floor_plan");
  const [error, setError] = useState<string | null>(null);

  const { job } = useJob(step === 3 ? jobId : null);

  useEffect(() => {
    if (job?.status === "complete" && step === 3) setStep(4);
  }, [job?.status, step]);

  async function handleCreateJob(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError(null);
    try {
      const created = await api.createJob(form);
      setJobId(created.id);
      setStep(2);
    } catch (err) { setError(String(err)); }
    finally { setCreating(false); }
  }

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files || !jobId) return;
    const newEntries: UploadEntry[] = Array.from(files).map((f) => ({
      name: f.name, assetType: activeTab, progress: 0, done: false,
    }));
    const startIdx = uploads.length;
    setUploads((prev) => [...prev, ...newEntries]);

    await Promise.all(
      Array.from(files).map((file, i) =>
        api.uploadDirect(jobId, activeTab, file, (pct) => {
          setUploads((prev) => prev.map((u, idx) => idx === startIdx + i ? { ...u, progress: pct } : u));
        })
        .then(() => setUploads((prev) => prev.map((u, idx) => idx === startIdx + i ? { ...u, done: true, progress: 100 } : u)))
        .catch((err: Error) => setUploads((prev) => prev.map((u, idx) => idx === startIdx + i ? { ...u, error: err.message } : u)))
      )
    );
  }, [jobId, activeTab, uploads.length]);

  async function handleStart() {
    if (!jobId) return;
    setStarting(true);
    setError(null);
    try {
      await api.startJob(jobId);
      setStep(3);
    } catch (err) { setError(String(err)); }
    finally { setStarting(false); }
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="flex-grow pt-24 pb-16 px-4 md:px-8 max-w-[1280px] mx-auto w-full flex flex-col items-center">
        <StepIndicator step={step} />

        {/* Step 1 — Property Details */}
        {step === 1 && (
          <div className="w-full max-w-4xl">
            <section className="bg-surface-container-lowest rounded-xl shadow-md border border-outline-variant p-8 md:p-12">
              <div className="mb-8">
                <h1 className="text-2xl font-extrabold text-on-surface tracking-tight mb-2">Create New Property Tour</h1>
                <p className="text-on-surface-variant text-sm">Provide the foundational data for your AI-powered property visualization.</p>
              </div>
              <form onSubmit={handleCreateJob} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                  {[
                    { id: "name", label: "Property Name *", placeholder: "ASSK Amari Maryland City", key: "name" as keyof PropertyInput, required: true },
                    { id: "developer", label: "Developer", placeholder: "ASSK Amari Way Developers Ltd.", key: "developer" as keyof PropertyInput },
                    { id: "location", label: "Location", placeholder: "F-Block, Aftabnagar, Dhaka", key: "location" as keyof PropertyInput },
                    { id: "unit_type", label: "Unit Type", placeholder: "e.g. Type A", key: "unit_type" as keyof PropertyInput },
                    { id: "area_sqft", label: "Area (sqft)", placeholder: "1362", key: "area_sqft" as keyof PropertyInput, type: "number" },
                    { id: "price_range", label: "Price Range", placeholder: "80–90 lakh BDT", key: "price_range" as keyof PropertyInput },
                  ].map((f) => (
                    <div key={f.id} className="flex flex-col gap-2">
                      <label className="text-sm font-bold text-on-surface" htmlFor={f.id}>{f.label}</label>
                      <input
                        id={f.id}
                        type={f.type ?? "text"}
                        required={f.required}
                        placeholder={f.placeholder}
                        value={(form[f.key] as string | number) ?? ""}
                        onChange={(e) => setForm((p) => ({ ...p, [f.key]: f.type === "number" ? parseInt(e.target.value) || undefined : e.target.value }))}
                        className="w-full bg-surface px-4 py-3 rounded-lg border border-outline focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all"
                      />
                    </div>
                  ))}
                </div>
                {error && <p className="text-sm text-error bg-error-container/30 rounded-lg px-3 py-2">{error}</p>}
                <div className="pt-8 border-t border-outline-variant flex justify-end">
                  <button type="submit" disabled={creating || !form.name} className="bg-primary-container hover:bg-primary text-on-primary-fixed-variant font-bold py-3 px-10 rounded-lg shadow-sm hover:shadow-md transition-all active:scale-95 disabled:opacity-60 flex items-center gap-2">
                    <span>{creating ? "Creating…" : "Create Job"}</span>
                    {!creating && <span className="material-symbols-outlined">arrow_forward</span>}
                  </button>
                </div>
              </form>
            </section>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              {[
                { icon: "description", title: "Data Precision", text: "Ensure sqft and price are accurate to help our AI generate realistic visualizations." },
                { icon: "speed",       title: "Processing Time", text: "Standard jobs process within 15–30 minutes depending on asset quality." },
                { icon: "security",    title: "Private Vault",   text: "Your uploaded blueprints are encrypted and stored securely." },
              ].map((c) => (
                <div key={c.title} className="bg-surface-container-high p-6 rounded-xl border border-outline-variant flex flex-col gap-3">
                  <span className="material-symbols-outlined text-primary">{c.icon}</span>
                  <h3 className="font-bold text-on-surface">{c.title}</h3>
                  <p className="text-xs text-on-surface-variant leading-relaxed">{c.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 2 — Upload Files */}
        {step === 2 && jobId && (
          <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-8 bg-surface-container-lowest rounded-xl shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] border border-outline-variant overflow-hidden">
              {/* Tabs */}
              <div className="flex border-b border-outline-variant">
                {(["floor_plan", "brochure", "photo"] as AssetType[]).map((t) => (
                  <button
                    key={t}
                    onClick={() => setActiveTab(t)}
                    className={`flex-1 py-4 px-6 text-sm font-bold transition-colors ${activeTab === t ? "text-primary border-b-2 border-primary bg-surface-container-low" : "text-on-surface-variant hover:bg-surface-container-lowest"}`}
                  >
                    {t === "floor_plan" ? "Floor Plan" : t === "brochure" ? "Brochure" : "Photos"}
                  </button>
                ))}
              </div>

              <div className="p-8">
                {/* Drop zone */}
                <label
                  className="relative group cursor-pointer border-2 border-dashed border-outline-variant rounded-xl p-12 flex flex-col items-center justify-center bg-surface-bright hover:bg-surface-container-low transition-all duration-300"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
                >
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <span className="material-symbols-outlined text-primary text-3xl">cloud_upload</span>
                  </div>
                  <h3 className="text-on-surface font-bold text-lg mb-2 text-center">
                    Drag and drop {activeTab === "floor_plan" ? "floor plans" : activeTab === "brochure" ? "brochure files" : "photos"} here
                  </h3>
                  <p className="text-on-surface-variant text-sm text-center mb-6">PDF, JPG, or PNG (up to {activeTab === "photo" ? "10" : "20"}MB)</p>
                  <span className="bg-primary text-on-primary px-6 py-2.5 rounded-lg font-bold text-sm shadow-sm hover:brightness-110 active:scale-95 transition-all">
                    Browse Files
                  </span>
                  <input type="file" multiple accept={ACCEPT[activeTab]} className="hidden" onChange={(e) => handleFiles(e.target.files)} />
                </label>

                {/* Upload list */}
                {uploads.length > 0 && (
                  <div className="mt-8 space-y-4">
                    <h4 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">
                      Files ({uploads.length})
                    </h4>
                    {uploads.map((u, i) => (
                      <div key={i} className="p-4 rounded-lg bg-surface border border-outline-variant flex flex-col gap-3">
                        <div className="flex justify-between items-start">
                          <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded flex items-center justify-center ${u.done ? "bg-secondary/10" : "bg-tertiary/10"}`}>
                              <span className={`material-symbols-outlined ${u.done ? "text-secondary" : "text-tertiary"}`}>
                                {u.assetType === "photo" ? "image" : "description"}
                              </span>
                            </div>
                            <div>
                              <p className="text-sm font-bold text-on-surface truncate max-w-[200px]">{u.name}</p>
                              <p className="text-xs text-on-surface-variant">
                                {u.error ? <span className="text-error">{u.error}</span> : u.done ? "Complete" : `${u.progress}% uploaded`}
                              </p>
                            </div>
                          </div>
                          {u.done && <span className="material-symbols-outlined text-secondary" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>}
                        </div>
                        {!u.done && !u.error && (
                          <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                            <div className="bg-primary-container h-full rounded-full transition-all" style={{ width: `${u.progress}%` }} />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="p-8 border-t border-outline-variant bg-surface flex justify-end gap-4">
                {error && <p className="text-sm text-error mr-auto self-center">{error}</p>}
                <button onClick={() => setStep(1)} className="px-6 py-2.5 rounded-lg border border-outline-variant text-on-surface font-bold hover:bg-surface-container-low transition-all">
                  Back
                </button>
                <button
                  onClick={handleStart}
                  disabled={starting || uploads.length === 0}
                  className="bg-primary-container text-on-primary-container px-8 py-2.5 rounded-lg font-bold shadow-md hover:brightness-105 active:scale-95 transition-all disabled:opacity-60 flex items-center gap-2"
                >
                  <span>{starting ? "Starting…" : "Generate Tour"}</span>
                  {!starting && <span className="material-symbols-outlined text-sm">auto_awesome</span>}
                </button>
              </div>
            </div>

            {/* Tips panel */}
            <div className="lg:col-span-4 space-y-6">
              <div className="bg-surface-container-lowest rounded-xl p-6 border border-outline-variant shadow-sm">
                <h3 className="font-bold text-on-surface mb-4 flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">lightbulb</span>
                  AI Optimization Tips
                </h3>
                <ul className="space-y-4">
                  {[
                    "High-resolution PDF floor plans produce the most accurate results.",
                    "Ensure text on floor plans is legible so AI can identify room names.",
                    "Upload the developer brochure for better narration and specs.",
                    "Construction photos add authenticity — buyers trust them.",
                  ].map((tip, i) => (
                    <li key={i} className="flex gap-3">
                      <div className="shrink-0 w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                      <p className="text-sm text-on-surface-variant">{tip}</p>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Step 3 — Processing */}
        {step === 3 && job && (
          <div className="max-w-2xl mx-auto bg-surface-container-lowest rounded-xl shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] p-12 border border-outline-variant flex flex-col items-center text-center w-full">
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
              {job.current_stage ? STAGE_LABELS[job.current_stage] ?? job.current_stage : "Processing your files…"}
            </h1>
            <p className="text-on-surface-variant max-w-sm mb-12">
              Our AI is synthesizing high-fidelity visualizations from your uploaded architectural data.
            </p>
            <div className="mb-4">
              <span className="text-6xl font-black text-primary tracking-tighter">{job.progress_pct}%</span>
            </div>
            <div className="w-full max-w-md bg-surface-container-high h-4 rounded-full overflow-hidden mb-8 p-1">
              <div className="h-full bg-primary-container rounded-full progress-bar-glow transition-all duration-500" style={{ width: `${job.progress_pct}%` }} />
            </div>
            {job.status === "failed" && (
              <p className="text-sm text-error mb-4">{job.error_message}</p>
            )}
            <p className="text-xs text-on-surface-variant italic">Please do not close this window while processing is active.</p>
          </div>
        )}

        {/* Step 4 — Done */}
        {step === 4 && (
          <div className="w-full max-w-xl bg-surface-container-lowest rounded-xl shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] p-12 flex flex-col items-center text-center border border-outline-variant/30">
            <div className="w-24 h-24 rounded-full bg-secondary-container flex items-center justify-center mb-8">
              <span className="material-symbols-outlined text-secondary text-5xl" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>
            </div>
            <h1 className="text-3xl font-extrabold text-on-surface mb-4 tracking-tight">Your tour is ready!</h1>
            <p className="text-on-surface-variant mb-10 max-w-sm">
              PropViz AI has successfully processed your assets and generated the interactive virtual property tour.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 w-full">
              <Link
                href={`/viewer/${jobId}`}
                className="flex-1 bg-primary-container hover:bg-primary text-on-primary-container hover:text-on-primary font-bold py-4 px-6 rounded-lg transition-all active:scale-95 shadow-sm flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined">visibility</span>
                Open Viewer
              </Link>
              <button
                onClick={() => router.push("/dashboard")}
                className="flex-1 border border-outline-variant hover:bg-surface-container-low text-on-surface-variant font-bold py-4 px-6 rounded-lg transition-all active:scale-95 flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined">dashboard</span>
                Go to Dashboard
              </button>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
