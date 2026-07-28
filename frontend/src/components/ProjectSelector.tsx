import { useCurrentProject } from "../hooks/useCurrentProject";

export function ProjectSelector() {
  const { projects, currentProject, setCurrentProjectId, loading } = useCurrentProject();

  if (loading) {
    return <span className="project-selector-empty">Loading projects...</span>;
  }
  if (projects.length === 0) {
    return <span className="project-selector-empty">No projects yet</span>;
  }

  return (
    <select
      className="project-selector"
      value={currentProject?.id ?? ""}
      onChange={(e) => setCurrentProjectId(e.target.value)}
    >
      {projects.map((p) => (
        <option key={p.id} value={p.id}>
          {p.code} — {p.name}
        </option>
      ))}
    </select>
  );
}
