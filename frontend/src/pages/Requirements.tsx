import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { documentsApi, requirementsApi, systemsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { DocumentItem, Requirement, RequirementPriority, RequirementStatus, SystemItem } from "../types";
import { SEVERITY_RANK } from "../utils/rank";

const PRIORITIES: RequirementPriority[] = ["low", "medium", "high", "critical"];
const STATUSES: RequirementStatus[] = [
  "open", "in_progress", "under_review", "verified", "closed", "not_applicable",
];

const UNASSIGNED_KEY = "__unassigned__";

interface RequirementGroup {
  key: string;
  document: DocumentItem | null;
  requirements: Requirement[];
  completePct: number;
}

// A requirement counts toward "complete" once it's verified, or it's been
// excluded from scope entirely (not applicable) -- mirrors how the project
// dashboard's gap analysis treats not-applicable requirements as "no gap".
function completionPct(requirements: Requirement[]): number {
  if (requirements.length === 0) return 0;
  const done = requirements.filter((r) => r.verified || r.status === "not_applicable").length;
  return Math.round((done / requirements.length) * 100);
}

function completionBadgeColor(pct: number): "red" | "yellow" | "green" {
  if (pct < 40) return "red";
  if (pct < 75) return "yellow";
  return "green";
}

export function Requirements() {
  const { currentProject } = useCurrentProject();
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [systems, setSystems] = useState<SystemItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const [reqCode, setReqCode] = useState("");
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState<RequirementPriority>("medium");
  const [systemId, setSystemId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deletePendingId, setDeletePendingId] = useState<string | null>(null);

  function load(projectId: string) {
    setLoading(true);
    Promise.all([requirementsApi.list(projectId), documentsApi.list(projectId), systemsApi.list(projectId)])
      .then(([reqs, docs, systemList]) => {
        setRequirements(reqs);
        setDocuments(docs);
        setSystems(systemList);
        const firstDocWithReqs = docs.find((d) => reqs.some((r) => r.document_id === d.id));
        if (firstDocWithReqs) {
          setExpanded({ [firstDocWithReqs.id]: true });
        } else if (reqs.some((r) => !r.document_id)) {
          setExpanded({ [UNASSIGNED_KEY]: true });
        } else {
          setExpanded({});
        }
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load requirements"))
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
      await requirementsApi.create({
        project_id: currentProject.id,
        req_code: reqCode,
        title,
        priority,
        system_id: systemId || null,
      });
      setReqCode("");
      setTitle("");
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create requirement");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusChange(requirementId: string, status: RequirementStatus) {
    setError(null);
    try {
      const updated = await requirementsApi.setStatus(requirementId, status);
      setRequirements((prev) => prev.map((r) => (r.id === requirementId ? updated : r)));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to update status");
    }
  }

  async function handleDelete(requirementId: string) {
    setError(null);
    try {
      await requirementsApi.remove(requirementId);
      setDeletePendingId(null);
      setRequirements((prev) => prev.filter((r) => r.id !== requirementId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete requirement");
    }
  }

  function systemName(id: string | null): string {
    if (!id) return "—";
    return systems.find((s) => s.id === id)?.name ?? id;
  }

  function toggle(key: string) {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  const groups = useMemo<RequirementGroup[]>(() => {
    const byDoc = new Map<string, Requirement[]>();
    for (const r of requirements) {
      const key = r.document_id ?? UNASSIGNED_KEY;
      const list = byDoc.get(key);
      if (list) list.push(r);
      else byDoc.set(key, [r]);
    }
    const docGroups: RequirementGroup[] = documents
      .filter((d) => byDoc.has(d.id))
      .map((d) => {
        const reqs = byDoc.get(d.id)!;
        return { key: d.id, document: d, requirements: reqs, completePct: completionPct(reqs) };
      });
    const unassigned = byDoc.get(UNASSIGNED_KEY);
    if (unassigned) {
      docGroups.push({
        key: UNASSIGNED_KEY,
        document: null,
        requirements: unassigned,
        completePct: completionPct(unassigned),
      });
    }
    return docGroups;
  }, [requirements, documents]);

  const requirementColumns = [
    { header: "ID", render: (r: Requirement) => r.req_code, sortValue: (r: Requirement) => r.req_code },
    {
      header: "Requirement",
      render: (r: Requirement) => (
        <Link to={`/requirements/${r.id}`} className="requirement-link">
          {r.title}
        </Link>
      ),
      sortValue: (r: Requirement) => r.title,
    },
    { header: "Category", render: (r: Requirement) => r.category || "—", sortValue: (r: Requirement) => r.category },
    {
      header: "System / Process",
      render: (r: Requirement) => systemName(r.system_id),
      sortValue: (r: Requirement) => systemName(r.system_id),
    },
    {
      header: "Criticality",
      render: (r: Requirement) => <span className={`badge badge-${r.priority}`}>{r.priority}</span>,
      sortValue: (r: Requirement) => SEVERITY_RANK[r.priority] ?? 0,
    },
    {
      header: "Recommended Verification",
      render: (r: Requirement) => r.verification_type || "—",
      sortValue: (r: Requirement) => r.verification_type,
    },
    {
      header: "Status",
      render: (r: Requirement) => (
        <select
          className={`status-select badge-${r.status}`}
          value={r.status}
          onChange={(e) => handleStatusChange(r.id, e.target.value as RequirementStatus)}
          onClick={(e) => e.stopPropagation()}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ")}
            </option>
          ))}
        </select>
      ),
      sortValue: (r: Requirement) => r.status,
    },
    {
      header: "",
      render: (r: Requirement) =>
        deletePendingId === r.id ? (
          <span className="inline-confirm">
            <button className="btn-danger" onClick={(e) => { e.stopPropagation(); handleDelete(r.id); }}>
              Confirm
            </button>
            <button className="btn-link" onClick={(e) => { e.stopPropagation(); setDeletePendingId(null); }}>
              Cancel
            </button>
          </span>
        ) : (
          <button className="btn-link" onClick={(e) => { e.stopPropagation(); setDeletePendingId(r.id); }}>
            Delete
          </button>
        ),
    },
  ];

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Requirements — {currentProject.name}</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <form className="form-inline" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="req-code">Req code</label>
          <input id="req-code" required placeholder="URS-001" value={reqCode} onChange={(e) => setReqCode(e.target.value)} />
        </div>
        <div className="form-row">
          <label htmlFor="req-title">Title</label>
          <input id="req-title" required value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="form-row">
          <label htmlFor="req-priority">Priority</label>
          <select id="req-priority" value={priority} onChange={(e) => setPriority(e.target.value as RequirementPriority)}>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <label htmlFor="req-system">System / Process</label>
          <select id="req-system" value={systemId} onChange={(e) => setSystemId(e.target.value)}>
            <option value="">— None —</option>
            {systems.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
        <button className="btn" type="submit" disabled={submitting}>
          Add requirement
        </button>
      </form>

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : groups.length === 0 ? (
        <p className="empty-state">No requirements yet.</p>
      ) : (
        <div className="requirement-groups">
          {groups.map((group) => {
            const isOpen = expanded[group.key] ?? false;
            const label = group.document ? `${group.document.doc_type} — ${group.document.name}` : "Unassigned Requirements";
            const count = group.requirements.length;
            return (
              <div className="card requirement-group" key={group.key}>
                <button
                  type="button"
                  className="requirement-group-header"
                  onClick={() => toggle(group.key)}
                  aria-expanded={isOpen}
                >
                  <span className="requirement-group-title">
                    <span className={"sidebar-group-chevron" + (isOpen ? " expanded" : "")}>▶</span>
                    {label}
                  </span>
                  <span className="requirement-group-meta">
                    {group.document?.version && <span className="badge">{group.document.version}</span>}
                    <span className={`badge badge-${completionBadgeColor(group.completePct)}`}>
                      {group.completePct}% complete
                    </span>
                    <span className="requirement-group-count">
                      {count} requirement{count === 1 ? "" : "s"}
                    </span>
                  </span>
                </button>
                {isOpen && (
                  <DataTable
                    rows={group.requirements}
                    rowKey={(r) => r.id}
                    emptyMessage="No requirements in this document."
                    columns={requirementColumns}
                  />
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
