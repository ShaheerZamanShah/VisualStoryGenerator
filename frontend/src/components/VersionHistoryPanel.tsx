type VersionItem = {
  version: number;
  timestamp: string;
  note: string;
};

type Props = {
  jobId?: string;
  versions: VersionItem[];
  loading: boolean;
  onRefresh: () => Promise<void>;
};

export default function VersionHistoryPanel({ jobId, versions, loading, onRefresh }: Props) {
  return (
    <section className="card">
      <div className="row row-space">
        <h3>Version History</h3>
        <button className="btn secondary" type="button" disabled={!jobId || loading} onClick={onRefresh}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>
      {!jobId && <p className="muted">Start a job to track edit snapshots and undo history.</p>}
      {jobId && versions.length === 0 && <p className="muted">No versions yet. Apply an edit to create snapshot v_1.</p>}
      {versions.length > 0 && (
        <ul className="history-list">
          {versions
            .slice()
            .reverse()
            .map((v) => (
              <li key={`${v.version}-${v.timestamp}`} className="history-item">
                <span className="history-version">v_{v.version}</span>
                <span className="history-note">{v.note || "edit"}</span>
                <time className="history-time">{new Date(v.timestamp).toLocaleString()}</time>
              </li>
            ))}
        </ul>
      )}
    </section>
  );
}
