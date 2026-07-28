import { useEffect, useState, type FormEvent } from "react";

import { DataTable } from "../components/DataTable";
import { ValidationTimeline } from "../components/ValidationTimeline";
import { useCurrentProject } from "../hooks/useCurrentProject";
import { validationActivitiesApi } from "../services/api";
import { ApiError } from "../services/apiClient";
import type { ValidationActivity, ValidationActivityType, ValidationStatus } from "../types";

const ACTIVITY_TYPES: ValidationActivityType[] = [
  "engineering_study", "fat", "sat", "commissioning", "iq", "oq", "pq", "final_report", "other",
];

const TYPE_LABELS: Record<ValidationActivityType, string> = {
  engineering_study: "Engineering Studies",
  fat: "FAT",
  sat: "SAT",
  commissioning: "Commissioning",
  iq: "IQ",
  oq: "OQ",
  pq: "PQ",
  final_report: "Final Report",
  other: "Other",
};

const STATUSES: ValidationStatus[] = [
  "not_started", "in_progress", "passed", "failed", "blocked", "not_applicable",
];

export function ValidationActivities() {
  const { currentProject } = useCurrentProject();
  const [activities, setActivities] = useState<ValidationActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);

  const [name, setName] = useState("");
  const [activityType, setActivityType] = useState<ValidationActivityType>("engineering_study");
  const [plannedDate, setPlannedDate] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load(projectId: string) {
    setLoading(true);
    validationActivitiesApi
      .list(projectId)
      .then(setActivities)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load validation activities"))
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
      await validationActivitiesApi.create({
        project_id: currentProject.id,
        name,
        activity_type: activityType,
        planned_date: plannedDate || null,
        start_date: startDate || null,
        end_date: endDate || null,
      });
      setName("");
      setPlannedDate("");
      setStartDate("");
      setEndDate("");
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create activity");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSeedStandardPhases() {
    if (!currentProject) return;
    setSeeding(true);
    setError(null);
    try {
      await validationActivitiesApi.seedStandardPhases(currentProject.id);
      load(currentProject.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to seed standard phases");
    } finally {
      setSeeding(false);
    }
  }

  async function handleFieldChange(
    activity: ValidationActivity,
    field: "status" | "planned_date" | "start_date" | "end_date",
    value: string,
  ) {
    setError(null);
    const previous = activities;
    const patch = field === "status" ? { status: value as ValidationStatus } : { [field]: value || null };
    setActivities((prev) => prev.map((a) => (a.id === activity.id ? { ...a, ...patch } : a)));
    try {
      const updated = await validationActivitiesApi.update(activity.id, patch);
      setActivities((prev) => prev.map((a) => (a.id === activity.id ? updated : a)));
    } catch (err) {
      setActivities(previous);
      setError(err instanceof ApiError ? err.message : "Failed to update activity");
    }
  }

  if (!currentProject) {
    return <p className="empty-state">Select or create a project first.</p>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Validation Activities — {currentProject.name}</h1>
        <button className="btn btn-secondary" disabled={seeding} onClick={handleSeedStandardPhases}>
          {seeding ? "Adding..." : "Add Standard C&Q Phases"}
        </button>
      </div>
      {error && <div className="page-error">{error}</div>}

      {loading ? (
        <div className="page-loading">Loading...</div>
      ) : (
        <>
          <h2 className="section-heading" style={{ marginTop: 0 }}>
            Execution Timeline
          </h2>
          <ValidationTimeline
            activities={activities}
            windowStart={currentProject.start_date}
            windowEnd={currentProject.target_end_date}
          />

          <form className="form-inline" onSubmit={handleSubmit}>
            <div className="form-row">
              <label htmlFor="va-name">Name</label>
              <input id="va-name" required value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="form-row">
              <label htmlFor="va-type">Type</label>
              <select
                id="va-type"
                value={activityType}
                onChange={(e) => setActivityType(e.target.value as ValidationActivityType)}
              >
                {ACTIVITY_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {TYPE_LABELS[t]}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-row">
              <label htmlFor="va-planned">Planned date</label>
              <input id="va-planned" type="date" value={plannedDate} onChange={(e) => setPlannedDate(e.target.value)} />
            </div>
            <div className="form-row">
              <label htmlFor="va-start">Start date</label>
              <input id="va-start" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </div>
            <div className="form-row">
              <label htmlFor="va-end">End date</label>
              <input id="va-end" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
            <button className="btn" type="submit" disabled={submitting}>
              Add activity
            </button>
          </form>

          <DataTable
            rows={activities}
            rowKey={(a) => a.id}
            emptyMessage="No validation activities yet. Click Add Standard C&Q Phases to get started."
            columns={[
              { header: "Name", render: (a) => a.name, sortValue: (a) => a.name },
              {
                header: "Type",
                render: (a) => TYPE_LABELS[a.activity_type],
                sortValue: (a) => a.activity_type,
              },
              {
                header: "Status",
                render: (a) => (
                  <select
                    className={`status-select badge-${a.status}`}
                    value={a.status}
                    onChange={(e) => handleFieldChange(a, "status", e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s.replace(/_/g, " ")}
                      </option>
                    ))}
                  </select>
                ),
                sortValue: (a) => a.status,
              },
              {
                header: "Planned",
                render: (a) => (
                  <input
                    type="date"
                    value={a.planned_date ?? ""}
                    onChange={(e) => handleFieldChange(a, "planned_date", e.target.value)}
                  />
                ),
                sortValue: (a) => a.planned_date ?? "",
              },
              {
                header: "Start",
                render: (a) => (
                  <input
                    type="date"
                    value={a.start_date ?? ""}
                    onChange={(e) => handleFieldChange(a, "start_date", e.target.value)}
                  />
                ),
                sortValue: (a) => a.start_date ?? "",
              },
              {
                header: "End",
                render: (a) => (
                  <input
                    type="date"
                    value={a.end_date ?? ""}
                    onChange={(e) => handleFieldChange(a, "end_date", e.target.value)}
                  />
                ),
                sortValue: (a) => a.end_date ?? "",
              },
            ]}
          />
        </>
      )}
    </div>
  );
}
