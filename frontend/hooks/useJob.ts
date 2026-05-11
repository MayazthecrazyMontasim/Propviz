"use client";
import { useEffect, useRef, useState } from "react";
import { api, Job } from "@/lib/api";

const POLL_INTERVAL_MS = 3000;
const TERMINAL_STATUSES = new Set(["complete", "failed"]);

export function useJob(jobId: string | null) {
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let cancelled = false;

    async function poll() {
      try {
        const data = await api.getJob(jobId!);
        if (!cancelled) {
          setJob(data);
          if (!TERMINAL_STATUSES.has(data.status)) {
            timerRef.current = setTimeout(poll, POLL_INTERVAL_MS);
          }
        }
      } catch (err) {
        if (!cancelled) setError(String(err));
      }
    }

    poll();

    return () => {
      cancelled = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [jobId]);

  return { job, error };
}
