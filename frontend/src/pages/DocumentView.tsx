import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { useCurrentProject } from "../hooks/useCurrentProject";
import { documentsApi, requirementsApi, systemsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { DocumentItem, Requirement, SystemItem } from "../types";

export function DocumentView() {
  const { id } = useParams<{ id: string }>();
  const { currentProject } = useCurrentProject();
  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [systems, setSystems] = useState<SystemItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentProject || !id) return;
    setLoading(true);
    setError(null);
    Promise.all([
      documentsApi.list(currentProject.id),
      requirementsApi.list(currentProject.id),
      systemsApi.list(currentProject.id),
    ])
      .then(([docs, reqs, systemList]) => {
        setDocument(docs.find((d) => d.id === id) ?? null);
        setRequirements(
          reqs
            .filter((r) => r.document_id === id)
            .sort((a, b) => a.req_code.localeCompare(b.req_code, undefined, { numeric: true })),
        );
        setSystems(systemList);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load document"))
      .finally(() => setLoading(false));
  }, [currentProject, id]);

  function systemName(sid: string | null): string {
    if (!sid) return "—";
    return systems.find((s) => s.id === sid)?.name ?? sid;
  }

  if (loading) return <div className="page-loading">Loading...</div>;
  if (error) return <div className="page-error">{error}</div>;
  if (!document) return <div className="page-error">Document not found.</div>;

  const assessedCount = requirements.filter((r) => r.risk).length;
  const verifiedCount = requirements.filter((r) => r.verified).length;

  return (
    <div>
      <Link to="/documents" className="back-link">
        ← Back to Documents
      </Link>
      <div className="page-header">
        <h1>{document.name}</h1>
      </div>
      <p className="page-subtitle">
        {document.doc_type} · v{document.version} · {systemName(document.system_id)}
      </p>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{requirements.length}</div>
          <div className="stat-label">Requirements</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{assessedCount}</div>
          <div className="stat-label">AI Assessed</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{verifiedCount}</div>
          <div className="stat-label">Verified</div>
        </div>
      </div>

      <h2 className="section-heading" style={{ marginTop: 8 }}>
        Requirements &amp; AI Assessment
      </h2>
      <p className="page-subtitle" style={{ marginTop: -4 }}>
        Every requirement extracted from this document, shown with the requirement text next to what the AI
        determined for it.
      </p>

      {requirements.length === 0 ? (
        <p className="empty-state">No requirements extracted from this document yet.</p>
      ) : (
        <div className="assessment-doc">
          {requirements.map((r) => (
            <div className="card assessment-entry" key={r.id}>
              <div className="assessment-entry-header">
                <div>
                  <span className="assessment-req-code">{r.req_code}</span>
                  <Link to={`/requirements/${r.id}`} className="requirement-link" style={{ marginLeft: 10 }}>
                    {r.title}
                  </Link>
                </div>
                <div className="requirement-group-meta">
                  <span className={`badge badge-${r.priority}`}>{r.priority}</span>
                  <span className={`badge badge-${r.status}`}>{r.status.replace(/_/g, " ")}</span>
                </div>
              </div>

              <p className="assessment-req-text">{r.description || "—"}</p>

              <div className="assessment-divider" />

              {r.risk ? (
                <div className="field-list">
                  <div className="field-row">
                    <span className="field-label">Risk</span>
                    <span className="field-value">
                      <span className={`badge badge-${r.risk}`}>{r.risk}</span>
                    </span>
                  </div>
                  <div className="field-row">
                    <span className="field-label">GMP Reference</span>
                    <span className="field-value">{r.gmp_reference || "—"}</span>
                  </div>
                  <div className="field-row">
                    <span className="field-label">Acceptance Criteria</span>
                    <span className="field-value field-value-left">{r.acceptance_criteria || "—"}</span>
                  </div>
                  <div className="field-row">
                    <span className="field-label">Suggested Test</span>
                    <span className="field-value field-value-left">{r.suggested_test || "—"}</span>
                  </div>
                  <div className="field-row">
                    <span className="field-label">Protocol Section</span>
                    <span className="field-value">{r.protocol_section || "—"}</span>
                  </div>
                  <div className="field-row">
                    <span className="field-label">Verification</span>
                    <span className="field-value">{r.verification_type || "—"}</span>
                  </div>
                </div>
              ) : (
                <p className="empty-state" style={{ padding: "6px 0 0" }}>
                  Not yet AI-assessed.
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
