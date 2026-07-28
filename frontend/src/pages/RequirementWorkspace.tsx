import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { requirementsApi, systemsApi, usersApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Requirement, RequirementAttachment, SystemItem, User } from "../types";

const DOCUMENT_TYPES = [
  "Functional Specification",
  "Design Specification",
  "Risk Assessment",
  "Test Protocol",
  "SOP",
  "Preventative Maintenance",
  "Work Instruction",
  "Other",
];

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export function RequirementWorkspace() {
  const { id } = useParams<{ id: string }>();

  const [requirement, setRequirement] = useState<Requirement | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [systems, setSystems] = useState<SystemItem[]>([]);
  const [attachments, setAttachments] = useState<RequirementAttachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionPending, setActionPending] = useState<string | null>(null);
  const [showAssignPicker, setShowAssignPicker] = useState(false);
  const [assignUserId, setAssignUserId] = useState("");

  const [docType, setDocType] = useState(DOCUMENT_TYPES[0]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function load() {
    if (!id) return;
    setLoading(true);
    requirementsApi
      .get(id)
      .then((req) =>
        Promise.all([
          Promise.resolve(req),
          requirementsApi.listAttachments(id),
          usersApi.list(),
          systemsApi.list(req.project_id),
        ]),
      )
      .then(([req, atts, userList, systemList]) => {
        setRequirement(req);
        setAttachments(atts);
        setUsers(userList);
        setSystems(systemList);
        setAssignUserId((prev) => prev || req.assigned_to_id || userList[0]?.id || "");
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load requirement"))
      .finally(() => setLoading(false));
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(load, [id]);

  async function runAction(name: string, action: () => Promise<Requirement>) {
    setActionPending(name);
    setError(null);
    try {
      setRequirement(await action());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : `${name} failed`);
    } finally {
      setActionPending(null);
    }
  }

  async function handleGenerateProtocol() {
    if (!id) return;
    setActionPending("generate-protocol");
    setError(null);
    try {
      const protocol = await requirementsApi.generateProtocol(id);
      alert(`Protocol ${protocol.protocol_number} generated with test steps.`);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Protocol generation failed");
    } finally {
      setActionPending(null);
    }
  }

  async function handleConfirmAssign() {
    if (!id || !assignUserId) return;
    await runAction("assign-owner", () => requirementsApi.assignOwner(id, assignUserId));
    setShowAssignPicker(false);
  }

  async function handleSystemChange(newSystemId: string) {
    if (!id) return;
    setError(null);
    try {
      setRequirement(await requirementsApi.setSystem(id, newSystemId || null));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to update system link");
    }
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Choose a file to upload");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      await requirementsApi.uploadAttachment(id, docType, file);
      if (fileInputRef.current) fileInputRef.current.value = "";
      const atts = await requirementsApi.listAttachments(id);
      setAttachments(atts);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  if (loading) return <div className="page-loading">Loading...</div>;
  if (!requirement) return <div className="page-error">{error ?? "Requirement not found."}</div>;

  const assignedUser = users.find((u) => u.id === requirement.assigned_to_id);
  const req = requirement;

  return (
    <div>
      <Link to="/requirements" className="back-link">
        ← Back to Requirements
      </Link>
      <div className="page-header">
        <h1>Requirement Workspace — {req.req_code}</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <div className="toolbar">
        <button className="btn" disabled={actionPending !== null} onClick={handleGenerateProtocol}>
          {actionPending === "generate-protocol" ? "Generating..." : "Generate Protocol"}
        </button>
        <button
          className="btn btn-secondary"
          disabled={actionPending !== null}
          onClick={() => setShowAssignPicker((v) => !v)}
        >
          Assign Owner
        </button>
        <button
          className="btn btn-secondary"
          disabled={actionPending !== null}
          onClick={() => runAction("mark-na", () => requirementsApi.markNa(id!))}
        >
          Mark N/A
        </button>
        <button
          className="btn btn-secondary"
          disabled={actionPending !== null}
          onClick={() => runAction("mark-under-review", () => requirementsApi.markUnderReview(id!))}
        >
          Mark Under Review
        </button>
        <button
          className="btn btn-secondary"
          disabled={actionPending !== null}
          onClick={() => runAction("verify", () => requirementsApi.verify(id!))}
        >
          Verify Requirement
        </button>
        <button
          className="btn btn-secondary"
          disabled={actionPending !== null}
          onClick={() => runAction("close", () => requirementsApi.close(id!))}
        >
          Close Requirement
        </button>
      </div>

      {showAssignPicker && (
        <div className="card" style={{ marginBottom: 20, display: "flex", gap: 10, alignItems: "flex-end" }}>
          <div className="form-row" style={{ marginBottom: 0 }}>
            <label htmlFor="assign-user">Assign to</label>
            <select id="assign-user" value={assignUserId} onChange={(e) => setAssignUserId(e.target.value)}>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name} ({u.email})
                </option>
              ))}
            </select>
          </div>
          <button className="btn" disabled={actionPending !== null} onClick={handleConfirmAssign}>
            Confirm
          </button>
          <button className="btn-link" onClick={() => setShowAssignPicker(false)}>
            Cancel
          </button>
        </div>
      )}

      <div className="workspace-grid">
        <div className="card">
          <h2>Requirement Details</h2>
          <div className="field-list">
            <div className="field-row">
              <span className="field-label">Requirement ID</span>
              <span className="field-value">{req.req_code}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Category</span>
              <span className="field-value">{req.category || "—"}</span>
            </div>
            <div className="field-row">
              <span className="field-label">System / Process</span>
              <span className="field-value">
                <select
                  className="status-select"
                  value={req.system_id ?? ""}
                  onChange={(e) => handleSystemChange(e.target.value)}
                >
                  <option value="">— None —</option>
                  {systems.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </span>
            </div>
            <div className="field-row">
              <span className="field-label">Criticality</span>
              <span className="field-value">
                <span className={`badge badge-${req.priority}`}>{req.priority}</span>
              </span>
            </div>
            <div className="field-row">
              <span className="field-label">Status</span>
              <span className="field-value">
                <span className={`badge badge-${req.status}`}>{req.status.replace(/_/g, " ")}</span>
              </span>
            </div>
            <div className="field-row">
              <span className="field-label">Disposition</span>
              <span className="field-value">{req.disposition.replace(/_/g, " ")}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Assigned To</span>
              <span className="field-value">{assignedUser?.full_name ?? "Unassigned"}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Verification</span>
              <span className="field-value">{req.verification_type || "—"}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Requirement Text</h2>
          <p style={{ whiteSpace: "pre-wrap" }}>{req.description || "—"}</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>AI Assessment</h2>
        {req.risk ? (
          <div className="field-list">
            <div className="field-row">
              <span className="field-label">Risk</span>
              <span className="field-value">
                <span className={`badge badge-${req.risk}`}>{req.risk}</span>
              </span>
            </div>
            <div className="field-row">
              <span className="field-label">GMP Reference</span>
              <span className="field-value">{req.gmp_reference || "—"}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Acceptance Criteria</span>
              <span className="field-value field-value-left">{req.acceptance_criteria || "—"}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Suggested Test</span>
              <span className="field-value field-value-left">{req.suggested_test || "—"}</span>
            </div>
            <div className="field-row">
              <span className="field-label">Protocol Section</span>
              <span className="field-value">{req.protocol_section || "—"}</span>
            </div>
          </div>
        ) : (
          <div>
            <p className="empty-state">No AI assessment yet.</p>
            <button
              className="btn"
              disabled={actionPending !== null}
              onClick={() => runAction("assess", () => requirementsApi.assess(id!))}
            >
              {actionPending === "assess" ? "Assessing..." : "Run AI Assessment"}
            </button>
          </div>
        )}
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Traceability</h2>
        <div className="field-list">
          <div className="field-row">
            <span className="field-label">Requirement ID</span>
            <span className="field-value">{req.req_code}</span>
          </div>
          <div className="field-row">
            <span className="field-label">System / Process</span>
            <span className="field-value">
              {systems.find((s) => s.id === req.system_id)?.name ?? "Not linked"}
            </span>
          </div>
          <div className="field-row">
            <span className="field-label">Protocol Section</span>
            <span className="field-value">{req.protocol_section || "—"}</span>
          </div>
          <div className="field-row">
            <span className="field-label">GMP Reference</span>
            <span className="field-value">{req.gmp_reference || "—"}</span>
          </div>
          <div className="field-row">
            <span className="field-label">Verification Strategy</span>
            <span className="field-value">{req.verification_type || "—"}</span>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Supporting Documentation</h2>
        <form className="form-inline" onSubmit={handleUpload}>
          <div className="form-row">
            <label htmlFor="doc-type">Document Type</label>
            <select id="doc-type" value={docType} onChange={(e) => setDocType(e.target.value)}>
              {DOCUMENT_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <label htmlFor="doc-file">File</label>
            <input id="doc-file" type="file" ref={fileInputRef} />
          </div>
          <button className="btn" type="submit" disabled={uploading}>
            {uploading ? "Uploading..." : "Upload Supporting Document"}
          </button>
        </form>
        {attachments.length === 0 ? (
          <p className="empty-state">No supporting documentation uploaded yet.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {attachments.map((a) => (
              <li key={a.id}>
                {a.file_name} <span style={{ color: "var(--color-text-muted)" }}>({a.document_type})</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <h2>Validation Tasks</h2>
        <div className="field-list">
          <div className="field-row">
            <span className="field-label">Current Status</span>
            <span className="field-value">
              <span className={`badge badge-${req.status}`}>{req.status.replace(/_/g, " ")}</span>
            </span>
          </div>
          <div className="field-row">
            <span className="field-label">Disposition</span>
            <span className="field-value">{req.disposition.replace(/_/g, " ")}</span>
          </div>
          <div className="field-row">
            <span className="field-label">Assigned To</span>
            <span className="field-value">{assignedUser?.full_name ?? "Unassigned"}</span>
          </div>
          <div className="field-row">
            <span className="field-label">Assigned Date</span>
            <span className="field-value">{formatDate(req.assigned_date)}</span>
          </div>
          <div className="field-row">
            <span className="field-label">Review Date</span>
            <span className="field-value">{formatDate(req.review_date)}</span>
          </div>
          <div className="field-row">
            <span className="field-label">Closed Date</span>
            <span className="field-value">{req.closed_date ? formatDate(req.closed_date) : "Not Closed"}</span>
          </div>
          <div className="field-row">
            <span className="field-label">Verified</span>
            <span className="field-value">{req.verified ? "✓ Yes" : "✗ No"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
