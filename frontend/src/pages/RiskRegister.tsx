import { useEffect, useState, type FormEvent } from "react";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { risksApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Risk, RiskSeverity } from "../types";
import { SEVERITY_RANK } from "../utils/rank";

const SEVERITIES: RiskSeverity[] = ["low", "medium", "high", "critical"];

export function RiskRegister() {
  const { currentProject } = useCurrentProject();
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [severity, setSeverity] = useState<RiskSeverity>("medium");
  const [likelihood, setLikelihood] = useState<RiskSeverity>("medium");
  const [submitting, setSubmitting] = useState(false);

  function load(projectId: string) {
    setLoading(true);
    risksApi
      .list(projectId)
      .then(setRisks)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load risks"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    if (currentProject) load(currentProject.id);
  }, [currentProject]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!currentProject) return;
    setSubmitting(true);
    setError(null);
    try {
      await risksApi.create({ project_id: currentProject.id, title, severity, likelihood });
      setTitle("");
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create risk");
    } finally {
      setSubmitting(false);
    }
  }

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Risk Register — {currentProject.name}</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <form className="form-inline" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="risk-title">Title</label>
          <input id="risk-title" required value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="form-row">
          <label htmlFor="risk-severity">Severity</label>
          <select id="risk-severity" value={severity} onChange={(e) => setSeverity(e.target.value as RiskSeverity)}>
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <label htmlFor="risk-likelihood">Likelihood</label>
          <select
            id="risk-likelihood"
            value={likelihood}
            onChange={(e) => setLikelihood(e.target.value as RiskSeverity)}
          >
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <button className="btn" type="submit" disabled={submitting}>
          Add risk
        </button>
      </form>

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={risks}
          rowKey={(r) => r.id}
          emptyMessage="No risks logged yet."
          columns={[
            { header: "Title", render: (r) => r.title, sortValue: (r) => r.title },
            {
              header: "Severity",
              render: (r) => <span className={`badge badge-${r.severity}`}>{r.severity}</span>,
              sortValue: (r) => SEVERITY_RANK[r.severity] ?? 0,
            },
            {
              header: "Likelihood",
              render: (r) => <span className={`badge badge-${r.likelihood}`}>{r.likelihood}</span>,
              sortValue: (r) => SEVERITY_RANK[r.likelihood] ?? 0,
            },
            { header: "Score", render: (r) => r.risk_score, sortValue: (r) => r.risk_score },
            {
              header: "Status",
              render: (r) => <span className={`badge badge-${r.status}`}>{r.status}</span>,
              sortValue: (r) => r.status,
            },
          ]}
        />
      )}
    </div>
  );
}
