import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { dashboardApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { DashboardMetrics, PortfolioProject } from "../types";

export function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    dashboardApi
      .get()
      .then(setMetrics)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  if (error) return <div className="page-error">{error}</div>;
  if (loading || !metrics) return <div className="page-loading">Loading dashboard...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Portfolio Dashboard</h1>
      </div>
      <p className="page-subtitle">
        Every project, its dependencies, and overall completion — click a project for its full readiness dashboard.
      </p>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{metrics.total_projects}</div>
          <div className="stat-label">Total Projects</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{metrics.open_risks}</div>
          <div className="stat-label">Open Risks (Portfolio-wide)</div>
        </div>
      </div>

      <h2 className="section-heading">Projects</h2>
      <DataTable
        rows={metrics.projects}
        rowKey={(p) => p.id}
        emptyMessage="No projects yet. Create one from the Projects page."
        columns={[
          { header: "Code", render: (p) => p.code, sortValue: (p) => p.code },
          {
            header: "Project",
            render: (p) => (
              <Link to={`/projects/${p.id}/dashboard`} className="requirement-link">
                {p.name}
              </Link>
            ),
            sortValue: (p) => p.name,
          },
          { header: "Client", render: (p) => p.client_name, sortValue: (p) => p.client_name },
          {
            header: "Status",
            render: (p) => <span className={`badge badge-${p.status}`}>{p.status.replace(/_/g, " ")}</span>,
            sortValue: (p) => p.status,
          },
          {
            header: "Completion",
            render: (p) => (
              <span className={`badge badge-${p.project_health}`}>{p.completion_pct}%</span>
            ),
            sortValue: (p) => p.completion_pct,
          },
          { header: "Current Stage", render: (p) => p.current_stage },
          {
            header: "Dependencies",
            render: (p: PortfolioProject) => (
              <span className="dependency-summary">
                <span title="Systems / Processes">{p.systems_count} systems</span>
                {" · "}
                <span title="Documents">{p.documents_count} docs</span>
                {" · "}
                <span title="Requirements">{p.requirements_count} reqs</span>
                {" · "}
                <span title="Validation Activities">{p.validation_activities_count} activities</span>
              </span>
            ),
          },
          {
            header: "Open Risks",
            render: (p) => (p.open_risks > 0 ? <span className="badge badge-high">{p.open_risks}</span> : "0"),
            sortValue: (p) => p.open_risks,
          },
        ]}
      />
    </div>
  );
}
