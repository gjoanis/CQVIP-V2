import { useEffect, useState, type FormEvent } from "react";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { systemsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { SystemItem, SystemType } from "../types";

const SYSTEM_TYPES: SystemType[] = [
  "equipment", "facility_system", "utility_system", "computerized_system", "process", "other",
];

export function Systems() {
  const { currentProject } = useCurrentProject();
  const [systems, setSystems] = useState<SystemItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [systemType, setSystemType] = useState<SystemType>("equipment");
  const [identifier, setIdentifier] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load(projectId: string) {
    setLoading(true);
    systemsApi
      .list(projectId)
      .then(setSystems)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load systems"))
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
      await systemsApi.create({
        project_id: currentProject.id,
        name,
        system_type: systemType,
        identifier,
      });
      setName("");
      setIdentifier("");
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create system");
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
        <h1>Systems &amp; Processes — {currentProject.name}</h1>
      </div>
      <p style={{ color: "var(--color-text-muted)", fontSize: "0.88rem", marginTop: -8 }}>
        Equipment, facility/utility systems, computerized systems, and manufacturing processes that
        URS/SOP/PM/Work Instruction documents and requirements trace back to.
      </p>
      {error && <div className="page-error">{error}</div>}

      <form className="form-inline" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="system-name">Name</label>
          <input
            id="system-name"
            required
            placeholder="HVAC System - Building Expansion"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <div className="form-row">
          <label htmlFor="system-type">Type</label>
          <select id="system-type" value={systemType} onChange={(e) => setSystemType(e.target.value as SystemType)}>
            {SYSTEM_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <label htmlFor="system-identifier">Identifier</label>
          <input
            id="system-identifier"
            placeholder="HVAC-001"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
          />
        </div>
        <button className="btn" type="submit" disabled={submitting}>
          Add system
        </button>
      </form>

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={systems}
          rowKey={(s) => s.id}
          emptyMessage="No systems or processes defined yet — add one above."
          columns={[
            { header: "Name", render: (s) => s.name, sortValue: (s) => s.name },
            { header: "Identifier", render: (s) => s.identifier || "—", sortValue: (s) => s.identifier },
            {
              header: "Type",
              render: (s) => <span className="badge">{s.system_type.replace(/_/g, " ")}</span>,
              sortValue: (s) => s.system_type,
            },
            { header: "Location", render: (s) => s.location || "—", sortValue: (s) => s.location },
          ]}
        />
      )}
    </div>
  );
}
