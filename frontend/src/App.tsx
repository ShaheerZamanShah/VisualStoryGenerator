import { useMemo, useState } from "react";
import EditPanel from "./components/EditPanel";
import PhaseProgress, { type ProgressEvent } from "./components/PhaseProgress";
import PromptForm from "./components/PromptForm";
import VideoPlayer from "./components/VideoPlayer";
import VersionHistoryPanel from "./components/VersionHistoryPanel";

const API_BASE =
  import.meta.env.VITE_API_BASE ??
  (import.meta.env.DEV ? "http://localhost:8001" : "");

function getWsBase(apiBase: string) {
  if (!apiBase) {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${proto}//${window.location.host}`;
  }
  try {
    const url = new URL(apiBase);
    return `${url.protocol === "https:" ? "wss:" : "ws:"}//${url.host}`;
  } catch {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${proto}//${window.location.host}`;
  }
}

export default function App() {
  const [jobId, setJobId] = useState<string>();
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [videoPath, setVideoPath] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [historyLoading, setHistoryLoading] = useState(false);
  const [versions, setVersions] = useState<Array<{ version: number; timestamp: string; note: string }>>([]);

  const socketBase = useMemo(() => getWsBase(API_BASE), []);
  const socketUrl = useMemo(() => (jobId ? `${socketBase}/ws/progress/${jobId}` : undefined), [jobId, socketBase]);

  const start = async (prompt: string) => {
    setLoading(true);
    setError(undefined);
    setEvents([]);
    setVersions([]);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Backend responded with ${res.status}: ${text}`);
      }

      const data = (await res.json()) as { job_id: string };
      setJobId(data.job_id);
      await fetchHistory(data.job_id);

      const ws = new WebSocket(`${socketBase}/ws/progress/${data.job_id}`);
      ws.onopen = () => ws.send("subscribe");
      ws.onmessage = (ev) => {
        const payload = JSON.parse(ev.data) as ProgressEvent;
        setEvents((prev) => [...prev, payload]);
        if (payload.phase === "error") {
          setError(String((payload.meta?.error as string) || payload.message || "Video generation failed."));
        }
        if (payload.phase === "done") {
          const path = String((payload.meta?.final_video_path as string) || "");
          if (path) {
            // Ensure the asset is available before setting src; try a few times to avoid race conditions.
            (async function waitForAsset(retries = 5) {
              const urlBase = `${API_BASE}/api/assets/${data.job_id}/final_output.mp4`;
              for (let i = 0; i < retries; i++) {
                try {
                  const head = await fetch(`${urlBase}?ts=${Date.now()}`, { method: "HEAD" });
                  if (head.ok) {
                    setVideoPath(`${urlBase}?ts=${Date.now()}`);
                    return;
                  }
                } catch (e) {
                  // ignore network errors and retry
                }
                await new Promise((res) => setTimeout(res, 500));
              }
              // Last resort: set the URL with cache-busting query param
              setVideoPath(`${API_BASE}/api/assets/${data.job_id}/final_output.mp4?ts=${Date.now()}`);
            })();
          }
        }
      };
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Failed to start pipeline.";
      setError(msg);
      console.error("Failed to start pipeline:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (incomingJobId?: string) => {
    const activeJobId = incomingJobId || jobId;
    if (!activeJobId) return;
    setHistoryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/edit/${activeJobId}/history`);
      if (!res.ok) {
        setVersions([]);
        return;
      }
      const data = (await res.json()) as { versions?: Array<{ version: number; timestamp: string; note: string }> };
      setVersions(data.versions || []);
    } finally {
      setHistoryLoading(false);
    }
  };

  const applyEdit = async (query: string) => {
    if (!jobId) return;
    await fetch(`${API_BASE}/api/edit/${jobId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    await fetchHistory();
  };

  const undo = async () => {
    if (!jobId) return;
    await fetch(`${API_BASE}/api/edit/${jobId}/undo`, { method: "POST" });
    await fetchHistory();
  };

  return (
    <main className="layout">
      <h1>AI-Powered Animated Video Generation</h1>
      <p className="sub">Dark-mode orchestration dashboard with real-time multi-agent progress.</p>
      <PromptForm onSubmit={start} loading={loading} />
      {error && <p className="error-banner">{error}</p>}
      <PhaseProgress events={events} />
      <VideoPlayer src={videoPath} />
      <EditPanel jobId={jobId} onApply={applyEdit} onUndo={undo} />
      <VersionHistoryPanel jobId={jobId} versions={versions} loading={historyLoading} onRefresh={fetchHistory} />
      {socketUrl && <small className="muted">WebSocket: {socketUrl}</small>}
    </main>
  );
}
