import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { requirementsApi, systemsApi, traceabilityApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Requirement, SystemItem, TraceabilityLink } from "../types";
import { SEVERITY_RANK } from "../utils/rank";

const ACTIVITY_TYPE_LABELS: Record<string, string> = {
  engineering_study: "Engineering Study",
  fat: "FAT",
  sat: "SAT",
  commissioning: "Commissioning",
  iq: "IQ",
  oq: "OQ",
  pq: "PQ",
  final_report: "Final Report",
  other: "Other",
};

export function TraceabilityMatrix() {
  const { currentProject } = useCurrentProject();
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [links, setLinks] = useState<TraceabilityLink[]>([]);
  const [systems, setSystems] = useState<SystemItem[]>([]);
  const [systemId, setSystemId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentProject) return;
    setLoading(true);
    Promise.all([
      requirementsApi.list(currentProject.id),
      traceabilityApi.matrix(currentProject.id),
      systemsApi.list(currentProject.id),
    ])
      .then(([reqs, matrixLinks, systemList]) => {
        setRequirements([...reqs].sort((a, b) => a.req_code.localeCompare(b.req_code, undefined, { numeric: true })));
        setLinks(matrixLinks);
        setSystems(systemList);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load traceability data"))
      .finally(() => setLoading(false));
  }, [currentProject]);

  const visibleRequirements = systemId ? requirements.filter((r) => r.system_id === systemId) : requirements;

  const testSectionsByRequirement = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const l of links) {
      if (!l.protocol_id) continue;
      const activityLabel = l.activity_type ? ACTIVITY_TYPE_LABELS[l.activity_type] ?? l.activity_type : null;
      const section = l.protocol_title || l.protocol_number;
      const entry = activityLabel && section ? `${activityLabel} — ${section}` : activityLabel || section;
      if (!entry) continue;
      const existing = map.get(l.requirement_id) ?? [];
      if (!existing.includes(entry)) existing.push(entry);
      map.set(l.requirement_id, existing);
    }
    return map;
  }, [links]);

  const coveredCount = visibleRequirements.filter((r) => testSectionsByRequirement.has(r.id)).length;

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Traceability Matrix — {currentProject.name}</h1>
      </div>
      <p className="page-subtitle">
        Every requirement and the protocol/test section that verifies it. Generate a protocol from a requirement's
        workspace to fill in its Test Section/Form.
      </p>
      {error && <div className="page-error">{error}</div>}

      <div className="form-row">
        <label htmlFor="trace-system">System / Process</label>
        <select id="trace-system" value={systemId} onChange={(e) => setSystemId(e.target.value)}>
          <option value="">All Systems / Processes</option>
          {systems.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{visibleRequirements.length}</div>
          <div className="stat-label">Total Requirements</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{coveredCount}</div>
          <div className="stat-label">Covered</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{visibleRequirements.length - coveredCount}</div>
          <div className="stat-label">Uncovered</div>
        </div>
      </div>

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={visibleRequirements}
          rowKey={(r) => r.id}
          emptyMessage="No requirements in this project yet."
          columns={[
            {
              header: "ID",
              render: (r) => (
                <Link to={`/requirements/${r.id}`} className="requirement-link">
                  {r.req_code}
                </Link>
              ),
              sortValue: (r) => r.req_code,
            },
            {
              header: "Requirement",
              render: (r) => (
                <Link to={`/requirements/${r.id}`} className="trace-req-text">
                  {r.description || r.title}
                </Link>
              ),
              sortValue: (r) => r.title,
            },
            {
              header: "Priority",
              render: (r) => <span className={`badge badge-${r.priority}`}>{r.priority}</span>,
              sortValue: (r) => SEVERITY_RANK[r.priority] ?? 0,
            },
            {
              header: "CQV Protocol",
              render: (r) => {
                const sections = testSectionsByRequirement.get(r.id);
                return sections ? sections.join(", ") : "—";
              },
            },
          ]}
        />
      )}
    </div>
  );
}
