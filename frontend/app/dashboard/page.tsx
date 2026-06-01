"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api, JobListItem, JobStatus } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

const STATUS_BADGE: Record<string, string> = {
  pending:        "bg-surface-container-high text-on-surface-variant border-outline-variant",
  ingesting:      "bg-tertiary/10 text-tertiary border-tertiary/20",
  parsing:        "bg-tertiary/10 text-tertiary border-tertiary/20",
  reconstructing: "bg-tertiary/10 text-tertiary border-tertiary/20",
  synthesizing:   "bg-tertiary/10 text-tertiary border-tertiary/20",
  postprocessing: "bg-tertiary/10 text-tertiary border-tertiary/20",
  complete:       "bg-secondary/10 text-secondary border-secondary/20",
  failed:         "bg-error/10 text-error border-error/20",
};

const STATUS_BAR: Record<string, string> = {
  complete: "bg-secondary", failed: "bg-error",
};

export default function DashboardPage() {
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    api.listJobs()
      .then(setJobs)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(jobId: string) {
    if (!confirm("Delete this job? This cannot be undone.")) return;
    setDeleting(jobId);
    try {
      await api.deleteJob(jobId);
      setJobs((prev) => prev.filter((j) => j.id !== jobId));
    } catch (e) {
      alert(`Delete failed: ${e}`);
    } finally {
      setDeleting(null);
    }
  }

  const stats = {
    total: jobs.length,
    complete: jobs.filter((j) => j.status === "complete").length,
    processing: jobs.filter((j) => !["complete", "failed", "pending"].includes(j.status)).length,
    failed: jobs.filter((j) => j.status === "failed").length,
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="flex-grow pt-24 pb-12 px-8 max-w-[1280px] mx-auto w-full">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <h1 className="text-3xl font-extrabold tracking-tight text-on-background">Dashboard</h1>
          <Link href="/upload" className="flex items-center gap-2 bg-primary-container text-on-primary px-6 py-2.5 rounded-xl font-bold shadow-sm hover:opacity-90 active:scale-95 transition-all">
            <span className="material-symbols-outlined">add</span>
            New Tour
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {[
            { label: "Total Jobs", value: stats.total, icon: "analytics", color: "text-primary", border: "" },
            { label: "Complete", value: stats.complete, icon: "check_circle", color: "text-secondary", border: "border-l-4 border-l-secondary" },
            { label: "Processing", value: stats.processing, icon: "sync", color: "text-tertiary", border: "border-l-4 border-l-tertiary" },
            { label: "Failed", value: stats.failed, icon: "error", color: "text-error", border: "border-l-4 border-l-error" },
          ].map((s) => (
            <div key={s.label} className={`bg-surface-container-lowest p-6 rounded-xl shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] border border-outline-variant ${s.border} flex flex-col gap-1`}>
              <span className="text-on-surface-variant text-sm font-medium">{s.label}</span>
              <div className="flex items-center justify-between mt-2">
                <span className={`text-3xl font-bold ${s.color}`}>{s.value}</span>
                <span className={`material-symbols-outlined text-3xl ${s.color}`}>{s.icon}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Jobs table */}
        <div className="bg-surface-container-lowest rounded-xl shadow-[0px_4px_6px_-1px_rgba(0,0,0,0.05)] border border-outline-variant overflow-hidden">
          <div className="p-6 border-b border-outline-variant">
            <h2 className="text-lg font-bold text-on-surface">Recent Property Jobs</h2>
          </div>

          {loading && <div className="p-12 text-center text-on-surface-variant animate-pulse">Loading jobs…</div>}
          {error && <div className="p-12 text-center text-error">{error}</div>}
          {!loading && !error && jobs.length === 0 && (
            <div className="p-16 text-center space-y-3">
              <p className="text-on-surface-variant">No tours yet.</p>
              <Link href="/upload" className="text-primary font-bold text-sm hover:underline">Create your first tour</Link>
            </div>
          )}
          {!loading && jobs.length > 0 && (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="bg-surface-container-low text-on-surface-variant text-xs uppercase tracking-wider">
                      <th className="px-6 py-4 font-semibold">Property Name</th>
                      <th className="px-6 py-4 font-semibold">Status</th>
                      <th className="px-6 py-4 font-semibold">Progress</th>
                      <th className="px-6 py-4 font-semibold text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant">
                    {jobs.map((job) => (
                      <tr key={job.id} className="hover:bg-surface-container-low/50 transition-colors">
                        <td className="px-6 py-4 font-medium text-on-surface">{job.property_name}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${STATUS_BADGE[job.status] ?? STATUS_BADGE.pending}`}>
                            {job.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-24 bg-outline-variant rounded-full h-1.5 overflow-hidden">
                              <div
                                className={`h-full rounded-full ${STATUS_BAR[job.status] ?? "bg-primary-container"}`}
                                style={{ width: `${job.progress_pct}%` }}
                              />
                            </div>
                            <span className="text-xs text-on-surface-variant">{job.progress_pct}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center gap-3 justify-end">
                            <Link
                              href={`/viewer/${job.id}`}
                              className={`font-bold text-sm flex items-center gap-1 ${job.status === "complete" ? "text-primary hover:underline" : "text-on-surface-variant hover:text-primary"}`}
                            >
                              {job.status === "complete" ? "View Tour" : "Monitor"}
                              <span className="material-symbols-outlined text-sm">
                                {job.status === "complete" ? "visibility" : "monitoring"}
                              </span>
                            </Link>
                            <button
                              onClick={() => handleDelete(job.id)}
                              disabled={deleting === job.id}
                              className="text-error hover:text-error/70 disabled:opacity-40 transition-colors"
                              title="Delete job"
                            >
                              <span className="material-symbols-outlined text-sm">delete</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="p-4 bg-surface-container-low px-8">
                <span className="text-on-surface-variant text-sm font-medium">
                  Showing {jobs.length} {jobs.length === 1 ? "property" : "properties"}
                </span>
              </div>
            </>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
