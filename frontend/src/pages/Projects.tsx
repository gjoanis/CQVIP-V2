import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { clientsApi, projectsApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { Client, Project } from "../types";

export function Projects() {
  const { refreshProjects } = useCurrentProject();
  const [projects, setProjects] = useState<Project[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [clientId, setClientId] = useState("");
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [startDate, setStartDate] = useState("");
  const [targetEndDate, setTargetEndDate] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    setLoading(true);
    Promise.all([projectsApi.list(), clientsApi.list()])
      .then(([projectList, clientList]) => {
        setProjects(projectList);
        setClients(clientList);
        if (!clientId && clientList.length > 0) setClientId(clientList[0].id);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load projects"))
      .finally(() => setLoading(false));
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(load, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await projectsApi.create({
        client_id: clientId,
        name,
        code,
        status: "planning",
        start_date: startDate || null,
        target_end_date: targetEndDate || null,
      });
      setName("");
      setCode("");
      setStartDate("");
      setTargetEndDate("");
      load();
      refreshProjects();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create project");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDateChange(project: Project, field: "start_date" | "target_end_date", value: string) {
    setError(null);
    const previous = projects;
    const newValue = value || null;
    setProjects((prev) => prev.map((p) => (p.id === project.id ? { ...p, [field]: newValue } : p)));
    try {
      const updated = await projectsApi.update(project.id, {
        client_id: project.client_id,
        name: project.name,
        code: project.code,
        description: project.description,
        status: project.status,
        start_date: field === "start_date" ? newValue : project.start_date,
        target_end_date: field === "target_end_date" ? newValue : project.target_end_date,
      });
      setProjects((prev) => prev.map((p) => (p.id === project.id ? updated : p)));
      refreshProjects();
    } catch (err) {
      setProjects(previous);
      setError(err instanceof ApiError ? err.message : "Failed to update project timeframe");
    }
  }

  function clientName(id: string): string {
    return clients.find((c) => c.id === id)?.name ?? id;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Projects</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      {clients.length === 0 && !loading ? (
        <p className="empty-state">Add a client first before creating a project.</p>
      ) : (
        <form className="form-inline" onSubmit={handleSubmit}>
          <div className="form-row">
            <label htmlFor="project-client">Client</label>
            <select id="project-client" value={clientId} onChange={(e) => setClientId(e.target.value)}>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <label htmlFor="project-name">Name</label>
            <input id="project-name" required value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="form-row">
            <label htmlFor="project-code">Code</label>
            <input id="project-code" required value={code} onChange={(e) => setCode(e.target.value)} />
          </div>
          <div className="form-row">
            <label htmlFor="project-start">Start date</label>
            <input id="project-start" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div className="form-row">
            <label htmlFor="project-target-end">Target completion</label>
            <input
              id="project-target-end"
              type="date"
              value={targetEndDate}
              onChange={(e) => setTargetEndDate(e.target.value)}
            />
          </div>
          <button className="btn" type="submit" disabled={submitting}>
            Add project
          </button>
        </form>
      )}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={projects}
          rowKey={(p) => p.id}
          emptyMessage="No projects yet."
          columns={[
            { header: "Code", render: (p) => p.code, sortValue: (p) => p.code },
            {
              header: "Name",
              render: (p) => (
                <Link to={`/projects/${p.id}/dashboard`} className="requirement-link">
                  {p.name}
                </Link>
              ),
              sortValue: (p) => p.name,
            },
            { header: "Client", render: (p) => clientName(p.client_id), sortValue: (p) => clientName(p.client_id) },
            {
              header: "Status",
              render: (p) => <span className={`badge badge-${p.status}`}>{p.status.replace(/_/g, " ")}</span>,
              sortValue: (p) => p.status,
            },
            {
              header: "Start Date",
              render: (p) => (
                <input
                  type="date"
                  value={p.start_date ?? ""}
                  onChange={(e) => handleDateChange(p, "start_date", e.target.value)}
                />
              ),
              sortValue: (p) => p.start_date ?? "",
            },
            {
              header: "Target Completion",
              render: (p) => (
                <input
                  type="date"
                  value={p.target_end_date ?? ""}
                  onChange={(e) => handleDateChange(p, "target_end_date", e.target.value)}
                />
              ),
              sortValue: (p) => p.target_end_date ?? "",
            },
          ]}
        />
      )}
    </div>
  );
}
