import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { useCurrentProject } from "../hooks/useCurrentProject";
import { documentsApi, requirementsApi, systemsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { DocumentItem, ExtractedRequirement, Requirement, SystemItem } from "../types";

const EXTRACTABLE_DOC_TYPES = new Set(["URS", "FS", "DS", "HDS", "SDS"]);

export function DocumentView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentProject } = useCurrentProject();
  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [systems, setSystems] = useState<SystemItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [extracting, setExtracting] = useState(false);
  const [candidates, setCandidates] = useState<ExtractedRequirement[] | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [accepting, setAccepting] = useState(false);

  const [deleteConfirming, setDeleteConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);

  function load() {
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
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentProject, id]);

  async function handleExtract() {
    if (!id) return;
    setExtracting(true);
    setError(null);
    try {
      const found = await documentsApi.extractRequirements(id);
      setCandidates(found);
      setSelected(new Set(found.map((_, i) => i)));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Extraction failed");
    } finally {
      setExtracting(false);
    }
  }

  function updateCandidate(index: number, fields: Partial<ExtractedRequirement>) {
    setCandidates((prev) => (prev ? prev.map((c, i) => (i === index ? { ...c, ...fields } : c)) : prev));
  }

  function toggleSelected(index: number) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  async function handleAccept() {
    if (!candidates || !currentProject || !document) return;
    const toCreate = candidates.filter((_, i) => selected.has(i));
    if (toCreate.length === 0) return;
    setAccepting(true);
    setError(null);
    try {
      await Promise.all(
        toCreate.map((c) =>
          requirementsApi.create({
            project_id: currentProject.id,
            document_id: document.id,
            system_id: document.system_id,
            req_code: c.req_code,
            title: c.title,
            description: c.description,
            category: c.category,
            source: document.name,
          }),
        ),
      );
      setCandidates(null);
      setSelected(new Set());
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save accepted requirements");
    } finally {
      setAccepting(false);
    }
  }

  async function handleDelete() {
    if (!id) return;
    setDeleting(true);
    setError(null);
    try {
      await documentsApi.delete(id);
      navigate("/documents");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete document");
      setDeleting(false);
    }
  }

  function systemName(sid: string | null): string {
    if (!sid) return "—";
    return systems.find((s) => s.id === sid)?.name ?? sid;
  }

  if (loading) return <div className="page-loading">Loading...</div>;
  if (error && !document) return <div className="page-error">{error}</div>;
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
        {deleteConfirming ? (
          <div className="reset-confirm-row">
            <span className="page-subtitle" style={{ margin: 0 }}>
              Delete this document and its {requirements.length} extracted requirement
              {requirements.length === 1 ? "" : "s"}?
            </span>
            <button className="btn-danger" disabled={deleting} onClick={handleDelete}>
              {deleting ? "Deleting..." : "Confirm Delete"}
            </button>
            <button className="btn-link" onClick={() => setDeleteConfirming(false)}>
              Cancel
            </button>
          </div>
        ) : (
          <button className="btn-danger" onClick={() => setDeleteConfirming(true)}>
            Delete Document
          </button>
        )}
      </div>
      <p className="page-subtitle">
        {document.doc_type} · v{document.version} · {systemName(document.system_id)}
      </p>
      {error && <div className="page-error">{error}</div>}

      {EXTRACTABLE_DOC_TYPES.has(document.doc_type.toUpperCase()) && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h2>Extract Requirements</h2>
          <p className="page-subtitle" style={{ marginTop: -4, marginBottom: 16 }}>
            Have AI read this document and propose candidate requirements. Nothing is saved until you review and
            accept them below.
          </p>
          <button className="btn" onClick={handleExtract} disabled={extracting}>
            {extracting ? "Reading document..." : "Extract Requirements"}
          </button>

          {candidates && (
            <div style={{ marginTop: 20 }}>
              {candidates.length === 0 ? (
                <p className="empty-state">No candidate requirements found in this document.</p>
              ) : (
                <>
                  <div className="toolbar">
                    <button
                      type="button"
                      className="btn"
                      disabled={accepting || selected.size === 0}
                      onClick={handleAccept}
                    >
                      {accepting ? "Saving..." : `Accept Selected (${selected.size})`}
                    </button>
                    <button type="button" className="btn-link" onClick={() => setCandidates(null)}>
                      Discard All
                    </button>
                  </div>
                  <div className="assessment-doc">
                    {candidates.map((c, i) => (
                      <div className="card assessment-entry" key={i}>
                        <div className="assessment-entry-header">
                          <label className="candidate-select-row">
                            <input
                              type="checkbox"
                              checked={selected.has(i)}
                              onChange={() => toggleSelected(i)}
                              aria-label={`Include ${c.req_code}`}
                            />
                            <input
                              className="fmea-step-input"
                              value={c.req_code}
                              onChange={(e) => updateCandidate(i, { req_code: e.target.value })}
                              aria-label="Requirement code"
                              style={{ maxWidth: 140, fontWeight: 700 }}
                            />
                            <input
                              className="fmea-step-input"
                              value={c.title}
                              onChange={(e) => updateCandidate(i, { title: e.target.value })}
                              aria-label="Title"
                            />
                          </label>
                        </div>
                        <div className="field-list">
                          <div className="field-row">
                            <span className="field-label">Description</span>
                            <textarea
                              className="field-value-left fmea-textarea"
                              value={c.description}
                              onChange={(e) => updateCandidate(i, { description: e.target.value })}
                            />
                          </div>
                          <div className="field-row">
                            <span className="field-label">Category</span>
                            <input
                              className="field-value"
                              value={c.category}
                              onChange={(e) => updateCandidate(i, { category: e.target.value })}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}

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
