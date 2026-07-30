import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { useCurrentProject } from "../hooks/useCurrentProject";
import { traceabilityApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { CoverageSummary, TraceabilityLink } from "../types";

interface MatrixRequirement {
  requirement_id: string;
  req_code: string;
  requirement_title: string;
}

interface MatrixProtocol {
  protocol_id: string;
  protocol_number: string;
  protocol_title: string;
}

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

  const requirements = useMemo<MatrixRequirement[]>(() => {
    const byId = new Map<string, MatrixRequirement>();
    for (const l of links) {
      if (!byId.has(l.requirement_id)) {
        byId.set(l.requirement_id, {
          requirement_id: l.requirement_id, req_code: l.req_code, requirement_title: l.requirement_title,
        });
      }
    }
    return [...byId.values()].sort((a, b) => a.req_code.localeCompare(b.req_code, undefined, { numeric: true }));
  }, [links]);

  const protocols = useMemo<MatrixProtocol[]>(() => {
    const byId = new Map<string, MatrixProtocol>();
    for (const l of links) {
      if (l.protocol_id && !byId.has(l.protocol_id)) {
        byId.set(l.protocol_id, {
          protocol_id: l.protocol_id, protocol_number: l.protocol_number ?? "",
          protocol_title: l.protocol_title ?? "",
        });
      }
    }
    return [...byId.values()].sort((a, b) =>
      a.protocol_number.localeCompare(b.protocol_number, undefined, { numeric: true }),
    );
  }, [links]);

  const cellMap = useMemo(() => {
    const map = new Map<string, TraceabilityLink>();
    for (const l of links) {
      if (l.protocol_id) map.set(`${l.requirement_id}::${l.protocol_id}`, l);
    }
    return map;
  }, [links]);

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Traceability Matrix — {currentProject.name}</h1>
      </div>
      <p className="page-subtitle">
        Each requirement against every protocol generated for it — a ✓ means that protocol traces back to and
        verifies that requirement. Generate a protocol from a requirement's workspace to add it here.
      </p>
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
      ) : requirements.length === 0 ? (
        <p className="empty-state">
          No traceability links yet. Open a requirement and click "Generate Protocol" to create one — it'll appear
          here as a column.
        </p>
      ) : (
        <div className="data-table-scroll">
          <table className="data-table trace-matrix">
            <thead>
              <tr>
                <th className="trace-matrix-corner">Requirement</th>
                {protocols.map((p) => (
                  <th key={p.protocol_id} title={p.protocol_title}>
                    {p.protocol_number}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {requirements.map((r) => (
                <tr key={r.requirement_id}>
                  <td className="trace-matrix-corner">
                    <Link to={`/requirements/${r.requirement_id}`} className="requirement-link">
                      {r.req_code}
                    </Link>
                    <div className="trace-req-title">{r.requirement_title}</div>
                  </td>
                  {protocols.map((p) => {
                    const link = cellMap.get(`${r.requirement_id}::${p.protocol_id}`);
                    return (
                      <td key={p.protocol_id} className="trace-cell">
                        {link && (
                          <span
                            className={`badge badge-${link.coverage_status}`}
                            title={link.test_step_description ?? undefined}
                          >
                            {link.coverage_status === "covered" ? "✓" : "○"}
                          </span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
