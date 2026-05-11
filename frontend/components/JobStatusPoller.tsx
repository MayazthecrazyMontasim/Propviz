"use client";
import { useJob } from "@/hooks/useJob";

const STAGE_LABELS: Record<string, string> = {
  ingest:          "Validating files",
  parse:           "Extracting floor plan & specs",
  reconstruct:     "Generating interior renders",
  synthesize:      "Creating narration audio",
  postprocess:     "Assembling final video",
};

const STATUS_COLORS: Record<string, string> = {
  pending:        "bg-gray-100 text-gray-600",
  ingesting:      "bg-blue-100 text-blue-700",
  parsing:        "bg-purple-100 text-purple-700",
  reconstructing: "bg-orange-100 text-orange-700",
  synthesizing:   "bg-yellow-100 text-yellow-700",
  postprocessing: "bg-indigo-100 text-indigo-700",
  complete:       "bg-green-100 text-green-700",
  failed:         "bg-red-100 text-red-700",
};

interface Props {
  jobId: string;
  onComplete?: (outputUrl: string) => void;
}

export function JobStatusPoller({ jobId, onComplete }: Props) {
  const { job, error } = useJob(jobId);

  if (error) return <p className="text-red-500 text-sm">{error}</p>;
  if (!job) return <p className="text-gray-400 text-sm animate-pulse">Loading job…</p>;

  if (job.status === "complete" && job.output_url) {
    onComplete?.(job.output_url);
  }

  const stageLabel = job.current_stage ? STAGE_LABELS[job.current_stage] ?? job.current_stage : null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span
          className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${STATUS_COLORS[job.status] ?? "bg-gray-100 text-gray-500"}`}
        >
          {job.status}
        </span>
        <span className="text-sm font-medium text-gray-600">{job.progress_pct}%</span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full bg-brand-500 rounded-full transition-all duration-500 ${
            job.status !== "complete" && job.status !== "failed" ? "progress-pulse" : ""
          }`}
          style={{ width: `${job.progress_pct}%` }}
        />
      </div>

      {stageLabel && (
        <p className="text-sm text-gray-500">{stageLabel}…</p>
      )}

      {job.status === "failed" && job.error_message && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {job.error_message}
        </p>
      )}

      {job.status === "complete" && (
        <p className="text-sm text-green-600 font-medium">
          Video ready!
        </p>
      )}
    </div>
  );
}
