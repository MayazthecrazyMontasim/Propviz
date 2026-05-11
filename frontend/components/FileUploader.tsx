"use client";
import { useCallback, useState } from "react";
import { api } from "@/lib/api";

type AssetType = "floor_plan" | "brochure" | "photo";

interface UploadedFile {
  name: string;
  assetType: AssetType;
  progress: number;
  done: boolean;
  error?: string;
}

interface Props {
  jobId: string;
  onAllUploaded?: () => void;
}

const ACCEPT: Record<AssetType, string> = {
  floor_plan: "image/jpeg,image/png,image/webp,application/pdf",
  brochure:   "image/jpeg,image/png,image/webp,application/pdf",
  photo:      "image/jpeg,image/png,image/webp",
};

const LABELS: Record<AssetType, string> = {
  floor_plan: "Floor Plan",
  brochure:   "Developer Brochure",
  photo:      "Construction Photos",
};

export function FileUploader({ jobId, onAllUploaded }: Props) {
  const [uploads, setUploads] = useState<UploadedFile[]>([]);
  const [activeType, setActiveType] = useState<AssetType>("floor_plan");

  const handleFiles = useCallback(
    async (files: FileList | null) => {
      if (!files || files.length === 0) return;

      const newUploads: UploadedFile[] = Array.from(files).map((f) => ({
        name: f.name,
        assetType: activeType,
        progress: 0,
        done: false,
      }));

      setUploads((prev) => [...prev, ...newUploads]);

      await Promise.all(
        Array.from(files).map((file, idx) =>
          api
            .uploadDirect(jobId, activeType, file, (pct) => {
              setUploads((prev) =>
                prev.map((u, i) =>
                  i === prev.length - files.length + idx ? { ...u, progress: pct } : u
                )
              );
            })
            .then(() => {
              setUploads((prev) =>
                prev.map((u, i) =>
                  i === prev.length - files.length + idx ? { ...u, done: true, progress: 100 } : u
                )
              );
            })
            .catch((err: Error) => {
              setUploads((prev) =>
                prev.map((u, i) =>
                  i === prev.length - files.length + idx ? { ...u, error: err.message } : u
                )
              );
            })
        )
      );

      const allDone = uploads.every((u) => u.done);
      if (allDone) onAllUploaded?.();
    },
    [jobId, activeType, uploads, onAllUploaded]
  );

  return (
    <div className="space-y-4">
      {/* Type selector */}
      <div className="flex gap-2">
        {(["floor_plan", "brochure", "photo"] as AssetType[]).map((t) => (
          <button
            key={t}
            onClick={() => setActiveType(t)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              activeType === t
                ? "bg-brand-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {LABELS[t]}
          </button>
        ))}
      </div>

      {/* Drop zone */}
      <label
        className="flex flex-col items-center justify-center w-full h-36 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
      >
        <svg className="w-8 h-8 text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <span className="text-sm text-gray-500">
          Drop {LABELS[activeType]} files here, or <span className="text-brand-500 font-medium">browse</span>
        </span>
        <input
          type="file"
          multiple
          accept={ACCEPT[activeType]}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </label>

      {/* Upload list */}
      {uploads.length > 0 && (
        <ul className="space-y-2">
          {uploads.map((u, i) => (
            <li key={i} className="flex items-center gap-3 text-sm">
              <span className="truncate flex-1 text-gray-700">{u.name}</span>
              <span className="text-xs text-gray-400 uppercase">{u.assetType}</span>
              {u.error ? (
                <span className="text-red-500 text-xs">{u.error}</span>
              ) : u.done ? (
                <span className="text-green-500 text-xs font-medium">Done</span>
              ) : (
                <div className="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-brand-500 transition-all"
                    style={{ width: `${u.progress}%` }}
                  />
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
