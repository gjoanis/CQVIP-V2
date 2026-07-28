import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { traceabilityApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { CoverageSummary, TraceabilityLink } from "../types";

export function TraceabilityMatrix() {
  const { currentProject } = useCurrentProject();
  const [links, setLinks] = useState<TraceabilityLink[]>([]);
  const [coverage, setCoverage] = useState<CoverageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentProject) return;
    setLoading(true);
    Promise.all([traceabilityApi.matrix(currentProject.id), traceabilityApi.coverage(currentProject.id)])
      .then(([matrixLinks, coverageSummary]) => {
        setLinks(matrixLinks);
        setCoverage(coverageSummary);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load traceability data"))
      .finally(() => setLoading(false));
  }, [currentProject]);

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Traceability Matrix — {currentProject.name}</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      {coverage && (
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-value">{coverage.total}</div>
            <div className="stat-label">Total links</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{coverage.covered}</div>
            <div className="stat-label">Covered</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{coverage.uncovered}</div>
            <div className="stat-label">Uncovered</div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={links}
          rowKey={(l) => l.id}
          emptyMessage="No traceability links yet. Link requirements to protocols/test steps via the API to populate this matrix."
          columns={[
            {
              header: "Requirement",
              render: (l) => (
                <Link to={`/requirements/${l.requirement_id}`} className="requirement-link">
                  {l.req_code}
                </Link>
              ),
              sortValue: (l) => l.req_code,
            },
            {
              header: "Protocol",
              render: (l) => (l.protocol_number ? `${l.protocol_number} — ${l.protocol_title}` : "—"),
              sortValue: (l) => l.protocol_number ?? "",
            },
            {
              header: "Test step",
              render: (l) => l.test_step_description || "—",
              sortValue: (l) => l.test_step_description ?? "",
            },
            {
              header: "Coverage",
              render: (l) => <span className={`badge badge-${l.coverage_status}`}>{l.coverage_status}</span>,
              sortValue: (l) => l.coverage_status,
            },
          ]}
        />
      )}
    </div>
  );
}
