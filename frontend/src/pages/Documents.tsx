import { useEffect, useRef, useState, type FormEvent } from "react";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { documentsApi, systemsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { DocumentItem, SystemItem } from "../types";

const DOC_TYPES = [
  "URS",
  "FS",
  "DS",
  "HDS",
  "SDS",
  "FAT",
  "SAT",
  "IQ",
  "OQ",
  "PQ",
  "COMMISSIONING",
  "PROTOCOL",
  "REPORT",
  "SOP",
  "PREVENTATIVE_MAINTENANCE",
  "WORK_INSTRUCTION",
];

export function Documents() {
  const { currentProject } = useCurrentProject();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [systems, setSystems] = useState<SystemItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [docType, setDocType] = useState(DOC_TYPES[0]);
  const [systemId, setSystemId] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function load(projectId: string) {
    setLoading(true);
    Promise.all([documentsApi.list(projectId), systemsApi.list(projectId)])
      .then(([docs, systemList]) => {
        setDocuments(docs);
        setSystems(systemList);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load documents"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    if (currentProject) load(currentProject.id);
  }, [currentProject]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!currentProject) return;
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Choose a file to upload");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      await documentsApi.upload(currentProject.id, docType, file, systemId || undefined);
      if (fileInputRef.current) fileInputRef.current.value = "";
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to upload document");
    } finally {
      setUploading(false);
    }
  }

  function systemName(id: string | null): string {
    if (!id) return "—";
    return systems.find((s) => s.id === id)?.name ?? id;
  }

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Documents — {currentProject.name}</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <form className="form-inline" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="doc-type">Document type</label>
          <select id="doc-type" value={docType} onChange={(e) => setDocType(e.target.value)}>
            {DOC_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <label htmlFor="doc-system">System / Process</label>
          <select id="doc-system" value={systemId} onChange={(e) => setSystemId(e.target.value)}>
            <option value="">— None —</option>
            {systems.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <label htmlFor="doc-file">File</label>
          <input id="doc-file" type="file" ref={fileInputRef} />
        </div>
        <button className="btn" type="submit" disabled={uploading}>
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </form>
      {systems.length === 0 && (
        <p className="empty-state">
          No systems defined yet — add one under Systems &amp; Processes to link documents to what they cover.
        </p>
      )}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={documents}
          rowKey={(d) => d.id}
          emptyMessage="No documents uploaded yet."
          columns={[
            { header: "Name", render: (d) => d.name, sortValue: (d) => d.name },
            { header: "Type", render: (d) => d.doc_type, sortValue: (d) => d.doc_type },
            {
              header: "System / Process",
              render: (d) => systemName(d.system_id),
              sortValue: (d) => systemName(d.system_id),
            },
            { header: "Version", render: (d) => d.version, sortValue: (d) => d.version },
            {
              header: "Status",
              render: (d) => <span className={`badge badge-${d.status}`}>{d.status}</span>,
              sortValue: (d) => d.status,
            },
          ]}
        />
      )}
    </div>
  );
}
