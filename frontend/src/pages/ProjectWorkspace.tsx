import { useEffect, useState, type FormEvent } from "react";

import { DataTable } from "../components/DataTable";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { projectWorkspaceApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { ProjectNode } from "../types";

const NODE_TYPES = ["folder", "document_link", "phase_link"] as const;

export function ProjectWorkspace() {
  const { currentProject } = useCurrentProject();
  const [nodes, setNodes] = useState<ProjectNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [nodeType, setNodeType] = useState<(typeof NODE_TYPES)[number]>("folder");
  const [submitting, setSubmitting] = useState(false);

  function load(projectId: string) {
    setLoading(true);
    projectWorkspaceApi
      .listNodes(projectId)
      .then(setNodes)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load workspace"))
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
      await projectWorkspaceApi.createNode(currentProject.id, { name, node_type: nodeType });
      setName("");
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create node");
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
        <h1>Project Workspace — {currentProject.name}</h1>
      </div>
      {error && <div className="page-error">{error}</div>}

      <form className="form-inline" onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="node-type">Type</label>
          <select
            id="node-type"
            value={nodeType}
            onChange={(e) => setNodeType(e.target.value as (typeof NODE_TYPES)[number])}
          >
            {NODE_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <label htmlFor="node-name">Name</label>
          <input id="node-name" required value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={submitting}>
          Add node
        </button>
      </form>

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <DataTable
          rows={nodes}
          rowKey={(n) => n.id}
          emptyMessage="No workspace nodes yet — add folders or links above."
          columns={[
            { header: "Name", render: (n) => n.name, sortValue: (n) => n.name },
            { header: "Type", render: (n) => n.node_type.replace(/_/g, " "), sortValue: (n) => n.node_type },
          ]}
        />
      )}
    </div>
  );
}
