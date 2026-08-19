import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { fmeaApi, systemsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { FmeaAnalysis, SystemItem } from "../types";

export function ProcessFmea() {
  const { currentProject } = useCurrentProject();
  const [analyses, setAnalyses] = useState<FmeaAnalysis[]>([]);
  const [systems, setSystems] = useState<SystemItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [systemId, setSystemId] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deletePendingId, setDeletePendingId] = useState<string | null>(null);

  function load(projectId: string) {
    setLoading(true);
    Promise.all([fmeaApi.list(projectId), systemsApi.list(projectId)])
      .then(([fmeaList, systemList]) => {
        setAnalyses(fmeaList);
        setSystems(systemList);
        if (!systemId && systemList.length > 0) setSystemId(systemList[0].id);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load Process FMEAs"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    if (currentProject) load(currentProject.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentProject]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!currentProject || !systemId) return;
    setSubmitting(true);
    setError(null);
    try {
      await fmeaApi.create({ project_id: currentProject.id, system_id: systemId, title, description });
      setTitle("");
      setDescription("");
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create Process FMEA");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(fmeaId: string) {
    setError(null);
    try {
      await fmeaApi.remove(fmeaId);
      setDeletePendingId(null);
      setAnalyses((prev) => prev.filter((a) => a.id !== fmeaId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete Process FMEA");
    }
  }

  function systemName(id: string): string {
    return systems.find((s) => s.id === id)?.name ?? id;
  }

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Process FMEA — {currentProject.name}</h1>
      </div>
      <p className="page-subtitle">
        Failure Mode and Effects Analysis for each System/Process — identify how a process step could fail, how
        severe/likely/detectable that failure is, and what to do about it.
      </p>
      {error && <div className="page-error">{error}</div>}

      {systems.length === 0 ? (
        <p className="empty-state">
          No Systems/Processes defined yet — add one under Systems &amp; Processes before starting an FMEA.
        </p>
      ) : (
        <form className="form-inline" onSubmit={handleSubmit}>
          <div className="form-row">
            <label htmlFor="fmea-system">System / Process</label>
            <select id="fmea-system" required value={systemId} onChange={(e) => setSystemId(e.target.value)}>
              {systems.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <label htmlFor="fmea-title">Title</label>
            <input
              id="fmea-title"
              required
              placeholder="e.g. Vial Filling Line 2 — Process FMEA"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div className="form-row">
            <label htmlFor="fmea-description">Description (optional)</label>
            <input id="fmea-description" value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "New Process FMEA"}
          </button>
        </form>
      )}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={analyses}
          rowKey={(a) => a.id}
          emptyMessage="No Process FMEAs started yet."
          columns={[
            {
              header: "Title",
              render: (a) => (
                <Link to={`/fmea/${a.id}`} className="requirement-link">
                  {a.title}
                </Link>
              ),
              sortValue: (a) => a.title,
            },
            {
              header: "System / Process",
              render: (a) => systemName(a.system_id),
              sortValue: (a) => systemName(a.system_id),
            },
            {
              header: "Status",
              render: (a) => <span className={`badge badge-${a.status}`}>{a.status.replace(/_/g, " ")}</span>,
              sortValue: (a) => a.status,
            },
            {
              header: "",
              render: (a) =>
                deletePendingId === a.id ? (
                  <span className="inline-confirm">
                    <button className="btn-danger" onClick={() => handleDelete(a.id)}>
                      Confirm
                    </button>
                    <button className="btn-link" onClick={() => setDeletePendingId(null)}>
                      Cancel
                    </button>
                  </span>
                ) : (
                  <button className="btn-link" onClick={() => setDeletePendingId(a.id)}>
                    Delete
                  </button>
                ),
            },
          ]}
        />
      )}
    </div>
  );
}
