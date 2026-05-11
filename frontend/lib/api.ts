import { API_BASE_URL } from "@/config/env";
import { getToken, clearToken } from "@/lib/auth";

export type JobStatus =
  | "pending" | "ingesting" | "parsing" | "reconstructing"
  | "synthesizing" | "postprocessing" | "complete" | "failed";

export interface Asset {
  id: string;
  asset_type: string;
  original_filename: string;
  cdn_url: string | null;
  size_bytes: number | null;
}

export interface Job {
  id: string;
  status: JobStatus;
  current_stage: string | null;
  progress_pct: number;
  output_url: string | null;
  error_message: string | null;
  assets: Asset[];
}

export interface JobListItem {
  id: string;
  status: JobStatus;
  progress_pct: number;
  output_url: string | null;
  property_name: string;
}

export interface PropertyInput {
  name: string;
  developer?: string;
  location?: string;
  unit_type?: string;
  area_sqft?: number;
  price_range?: string;
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...init?.headers,
    },
    ...init,
  });
  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  login: async (email: string, password: string): Promise<string> => {
    const form = new URLSearchParams({ username: email, password });
    const res = await fetch(`${API_BASE_URL}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
    if (!res.ok) throw new Error("Invalid email or password");
    const data = await res.json();
    return data.access_token;
  },

  createJob: (property: PropertyInput) =>
    request<Job>("/jobs/", { method: "POST", body: JSON.stringify({ property }) }),

  listJobs: () => request<JobListItem[]>("/jobs/"),

  getJob: (jobId: string) => request<Job>(`/jobs/${jobId}`),

  startJob: (jobId: string) =>
    request<Job>(`/jobs/${jobId}/start`, { method: "POST" }),

  deleteJob: (jobId: string) =>
    fetch(`${API_BASE_URL}/jobs/${jobId}`, {
      method: "DELETE",
      headers: authHeaders(),
    }),

  uploadDirect: async (
    jobId: string,
    assetType: string,
    file: File,
    onProgress?: (pct: number) => void
  ): Promise<{ asset_id: string; cdn_url: string }> => {
    const form = new FormData();
    form.append("job_id", jobId);
    form.append("asset_type", assetType);
    form.append("file", file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${API_BASE_URL}/assets/upload`);
      const token = getToken();
      if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) onProgress?.(Math.round((e.loaded / e.total) * 100));
      };
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText));
        else reject(new Error(`Upload failed: ${xhr.status}`));
      };
      xhr.onerror = () => reject(new Error("Network error during upload"));
      xhr.send(form);
    });
  },
};
