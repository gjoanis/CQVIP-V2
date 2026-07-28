import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { DataTable } from "../components/DataTable";
import { ValidationTimeline } from "../components/ValidationTimeline";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { projectDashboardApi, requirementsApi, validationActivitiesApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type {
  ActionQueueRow,
  GapAnalysisRow,
  ProjectDashboard as ProjectDashboardData,
  Requirement,
  ValidationActivity,
} from "../types";
import { SEVERITY_RANK } from "../utils/rank";

const PREVIEW_LIMIT = 15;
const DAY_MS = 24 * 60 * 60 * 1000;

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(`${value}T00:00:00`).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function ProjectDashboard() {
  const { projectId } = useParams<{ projectId: string }>();
  const { projects, setCurrentProjectId, loading: projectsLoading } = useCurrentProject();
  const [dashboard, setDashboard] = useState<ProjectDashboardData | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [gapRows, setGapRows] = useState<GapAnalysisRow[]>([]);
  const [actionRows, setActionRows] = useState<ActionQueueRow[]>([]);
  const [activities, setActivities] = useState<ValidationActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Visiting a project's dashboard also becomes the app's global "current
  // project" so navigating elsewhere (Documents, Requirements, ...) stays on it.
  useEffect(() => {
    if (projectId) setCurrentProjectId(projectId);
  }, [projectId, setCurrentProjectId]);

  const activeProject = projectId ? projects.find((p) => p.id === projectId) ?? null : null;

  useEffect(() => {
    if (!activeProject) return;
    setLoading(true);
    setError(null);
    Promise.all([
      projectDashboardApi.get(activeProject.id),
      requirementsApi.list(activeProject.id),
      projectDashboardApi.gapAnalysis(activeProject.id),
      projectDashboardApi.actionQueue(activeProject.id),
      validationActivitiesApi.list(activeProject.id),
    ])
      .then(([dash, reqs, gaps, actions, validationActivities]) => {
        setDashboard(dash);
        setRequirements(reqs);
        setGapRows(gaps);
        setActionRows(actions);
        setActivities(validationActivities);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, [activeProject]);

  if (!activeProject) {
    if (!projectsLoading) {
      return <div className="page-error">Project not found.</div>;
    }
    return <div className="page-loading">Loading...</div>;
  }
  if (error) return <div className="page-error">{error}</div>;
  if (loading || !dashboard) return <div className="page-loading">Loading dashboard...</div>;

  const requirementsPreview = [...requirements]
    .sort((a, b) => (SEVERITY_RANK[b.priority] ?? 0) - (SEVERITY_RANK[a.priority] ?? 0))
    .filter((r) => !r.verified && r.status !== "not_applicable")
    .slice(0, PREVIEW_LIMIT);

  const hasTimeframe = Boolean(activeProject.start_date || activeProject.target_end_date);
  let timeRemainingValue = "No target set";
  let timeRemainingLabel = "Time Remaining";
  if (activeProject.target_end_date) {
    const target = new Date(`${activeProject.target_end_date}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffDays = Math.round((target.getTime() - today.getTime()) / DAY_MS);
    if (diffDays > 0) {
      timeRemainingValue = `${diffDays} day${diffDays === 1 ? "" : "s"}`;
    } else if (diffDays === 0) {
      timeRemainingValue = "Due today";
    } else {
      timeRemainingValue = `${Math.abs(diffDays)} day${Math.abs(diffDays) === 1 ? "" : "s"} overdue`;
      timeRemainingLabel = "Past Target Completion";
    }
  }

  return (
    <div>
      <Link to="/" className="back-link">
        ← Back to Dashboard
      </Link>
      <div className="page-header">
        <h1>Quality Compliance Readiness Dashboard — {activeProject.name}</h1>
      </div>
      <p className="page-subtitle">AI-powered project readiness, inspection readiness, and compliance intelligence.</p>

      <h2 className="section-heading" style={{ marginTop: 0 }}>
        Project Timeframe
      </h2>
      {hasTimeframe ? (
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-value stat-value-text">{formatDate(activeProject.start_date)}</div>
            <div className="stat-label">Project Start</div>
          </div>
          <div className="stat-card">
            <div className="stat-value stat-value-text">{formatDate(activeProject.target_end_date)}</div>
            <div className="stat-label">Target Completion</div>
          </div>
          <div className="stat-card">
            <div className="stat-value stat-value-text">{timeRemainingValue}</div>
            <div className="stat-label">{timeRemainingLabel}</div>
          </div>
        </div>
      ) : (
        <div className="page-info">
          No project timeframe set yet. <Link to="/projects">Set a start and target completion date</Link> to see how
          much runway validation execution has to work with.
        </div>
      )}

      <ValidationTimeline
        activities={activities}
        windowStart={activeProject.start_date}
        windowEnd={activeProject.target_end_date}
      />

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{dashboard.lifecycle_readiness_pct}%</div>
          <div className="stat-label">Validation Lifecycle Readiness</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{dashboard.inspection_readiness_index_pct}%</div>
          <div className="stat-label">Inspection Readiness Index (IRI)</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{dashboard.execution_readiness_pct}%</div>
          <div className="stat-label">Validation Execution Readiness</div>
        </div>
        <div className="stat-card">
          <div className="stat-value stat-value-text">{dashboard.current_stage}</div>
          <div className="stat-label">Current Lifecycle Stage</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            <span className={`badge badge-lg badge-${dashboard.project_health}`}>
              {dashboard.project_health.toUpperCase()}
            </span>
          </div>
          <div className="stat-label">Project Health</div>
        </div>
      </div>

      <h2 className="section-heading">Phase Readiness</h2>
      <div className="stat-grid">
        {dashboard.phase_readiness.map((p) => (
          <div className="stat-card" key={p.phase}>
            <div className="stat-label" style={{ marginBottom: 4 }}>
              Phase {p.phase}
            </div>
            <div className="stat-value">{p.pct}%</div>
            <div className="stat-label">{p.label}</div>
          </div>
        ))}
      </div>

      <h2 className="section-heading">Requirements Needing Attention</h2>
      <DataTable
        rows={requirementsPreview}
        rowKey={(r) => r.id}
        emptyMessage="Nothing outstanding — every requirement is verified."
        columns={[
          { header: "ID", render: (r) => r.req_code },
          {
            header: "Requirement",
            render: (r) => (
              <Link to={`/requirements/${r.id}`} className="requirement-link">
                {r.title}
              </Link>
            ),
          },
          { header: "Category", render: (r) => r.category || "—" },
          {
            header: "Criticality",
            render: (r) => <span className={`badge badge-${r.priority}`}>{r.priority}</span>,
          },
          { header: "Recommended Verification", render: (r) => r.verification_type || "—" },
          {
            header: "Status",
            render: (r) => <span className={`badge badge-${r.status}`}>{r.status.replace(/_/g, " ")}</span>,
          },
        ]}
      />
      {requirements.length > requirementsPreview.length && (
        <p style={{ marginTop: 10 }}>
          <Link to="/requirements">View all {requirements.length} requirements →</Link>
        </p>
      )}

      <div className="card" style={{ margin: "24px 0" }}>
        <h2>AI Executive Summary</h2>
        <p style={{ whiteSpace: "pre-wrap" }}>{dashboard.executive_summary}</p>
      </div>

      <h2 className="section-heading">Gap Analysis</h2>
      <p className="page-subtitle" style={{ marginTop: -4 }}>
        AI-generated assessment of validation gaps, risk, priority, and required verification.
      </p>
      <DataTable
        rows={gapRows.filter((r) => r.gap !== "None").slice(0, PREVIEW_LIMIT)}
        rowKey={(r) => r.requirement_id}
        emptyMessage="No gaps identified."
        columns={[
          { header: "Requirement", render: (r) => r.req_code },
          { header: "Category", render: (r) => r.category || "—" },
          {
            header: "Criticality",
            render: (r) => <span className={`badge badge-${r.priority}`}>{r.priority}</span>,
          },
          {
            header: "Status",
            render: (r) => <span className={`badge badge-${r.status}`}>{r.status.replace(/_/g, " ")}</span>,
          },
          { header: "Gap", render: (r) => r.gap },
          { header: "Risk", render: (r) => <span className={`badge badge-${r.risk}`}>{r.risk}</span> },
          { header: "Recommendation", render: (r) => r.recommendation },
        ]}
      />
      {gapRows.filter((r) => r.gap !== "None").length > PREVIEW_LIMIT && (
        <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem", marginTop: 10 }}>
          Showing {PREVIEW_LIMIT} of {gapRows.filter((r) => r.gap !== "None").length} open gaps.
        </p>
      )}

      <h2 className="section-heading">Validation Action Queue</h2>
      <p className="page-subtitle" style={{ marginTop: -4 }}>
        Prioritized validation work generated from open requirements and identified gaps.
      </p>
      <DataTable
        rows={actionRows.slice(0, PREVIEW_LIMIT)}
        rowKey={(r) => r.requirement_id}
        emptyMessage="No outstanding action items."
        columns={[
          {
            header: "Priority",
            render: (r) => <span className={`badge badge-${r.priority}`}>{r.priority}</span>,
          },
          { header: "Requirement", render: (r) => r.req_code },
          { header: "Action Required", render: (r) => r.action_required },
          { header: "Owner", render: (r) => r.owner_name },
          {
            header: "Status",
            render: (r) => <span className={`badge badge-${r.status}`}>{r.status.replace(/_/g, " ")}</span>,
          },
        ]}
      />
      {actionRows.length > PREVIEW_LIMIT && (
        <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem", marginTop: 10 }}>
          Showing {PREVIEW_LIMIT} of {actionRows.length} action items.
        </p>
      )}
    </div>
  );
}
